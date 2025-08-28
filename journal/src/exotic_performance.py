import pytz
from datetime import date, time, datetime, timedelta, timezone
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import Trade, Candle, Transaction

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from yahoofinance import YahooTicker

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def getCandles(trade:Trade, timeframe='1m') -> list[Candle]:
    
    start_datetime = datetime.combine(trade.entry_date, datetime.strptime(trade.entry_time, '%H:%M:%S').time())
    end_datetime = datetime.combine(trade.exit_date, datetime.strptime(trade.exit_time, '%H:%M:%S').time())

    candles = session.query(Candle).filter(
        Candle.symbol == trade.symbol,
        Candle.date >= start_datetime,
        Candle.date <= end_datetime + timedelta(minutes=1),
        Candle.timeframe == timeframe
    ).all()

    if not candles:
        print(f'No candles data between {start_datetime} and {end_datetime}')
        return []
    
    return candles

def get_transaction_datetime(tx:Transaction) -> datetime:
    # Combinar fecha (date) con hora UTC (time)
    time_str = tx.time or '00:00:00'
    # Asegurar que tenga formato HH:MM:SS
    if len(time_str.split(':')) == 2:
        time_str += ':00'
    
    naive_dt = datetime.combine(tx.date, datetime.strptime(time_str, '%H:%M:%S').time())
    # Convertir a UTC ya que las horas están en UTC
    return naive_dt.replace(tzinfo=timezone.utc)

def getStartEndDatetime(trade:Trade) -> tuple[datetime, datetime, list[Transaction]]:

    sorted_transactions = sorted(trade.transactions, key=get_transaction_datetime)

    # Obtener el rango de tiempo
    start_datetime = get_transaction_datetime(sorted_transactions[0]) - timedelta(minutes=1)
    end_datetime = get_transaction_datetime(sorted_transactions[-1]) + timedelta(minutes=1)

    return start_datetime, end_datetime, sorted_transactions

def equity_curve(trade:Trade, initial_balance: float = 0):
    if not trade.transactions:
        return []

    start_datetime, end_datetime, sorted_transactions = getStartEndDatetime(trade=trade)

    # Buscar candles en el rango (date ya es datetime con UTC)
    candles = getCandles(trade, timeframe='1m')

    # Preparar DataFrame de candles
    df_candles = pd.DataFrame([c.to_dict() for c in candles])
    # date ya es datetime UTC, solo necesitamos asegurar que es datetime
    df_candles['datetime'] = pd.to_datetime(df_candles['date'], utc=True)
    df_candles.set_index('datetime', inplace=True)
    df_candles.sort_index(inplace=True)

    # Crear lista de transacciones con datetime completo
    transactions_with_dt = []
    for tx in sorted_transactions:
        tx_dt = get_transaction_datetime(tx)
        transactions_with_dt.append({
            'datetime': tx_dt,
            'transaction': tx
        })

    equity_points = []
    cash_balance = initial_balance  # Dinero en efectivo disponible
    position = 0  # Cantidad de acciones/contratos
    avg_price = 0  # Precio promedio de entrada
    commission_total = 0
    tx_index = 0
    
    # Inicializar current_time
    current_time = start_datetime # + timedelta(minutes=1)

    while current_time <= end_datetime:
        # Ejecutar transacciones hasta este momento
        while tx_index < len(transactions_with_dt):
            tx_data = transactions_with_dt[tx_index]
            tx_time = tx_data['datetime']
            tx: Transaction = tx_data['transaction']
            
            if tx_time > current_time:
                break

            commission = tx.commission or 0
            commission_total += commission
            cash_balance -= commission  # Las comisiones siempre reducen el cash

            if tx.type == trade.trade_type:  # Transacción de entrada (compra para LONG, venta para SHORT)
                if trade.trade_type == 'LONG':
                    # COMPRA: gastamos dinero, aumentamos posición
                    cost = tx.price * tx.quantity
                    cash_balance -= cost
                    
                    if position > 0:
                        # Recalcular precio promedio ponderado
                        total_cost = avg_price * position + tx.price * tx.quantity
                        position += tx.quantity
                        avg_price = total_cost / position
                    else:
                        position = tx.quantity
                        avg_price = tx.price
                        
                else:  # SHORT
                    # VENTA EN CORTO: recibimos dinero, aumentamos posición corta
                    proceeds = tx.price * tx.quantity
                    cash_balance += proceeds
                    
                    if position > 0:
                        # Recalcular precio promedio ponderado para posición corta
                        total_proceeds = avg_price * position + tx.price * tx.quantity
                        position += tx.quantity
                        avg_price = total_proceeds / position
                    else:
                        position = tx.quantity
                        avg_price = tx.price
                        
            else:  # Transacción de salida (venta para LONG, compra para SHORT)
                if trade.trade_type == 'LONG':
                    # VENTA: recibimos dinero, reducimos posición
                    proceeds = tx.price * tx.quantity
                    cash_balance += proceeds
                    position -= tx.quantity
                    
                else:  # SHORT
                    # COMPRA PARA CERRAR CORTO: gastamos dinero, reducimos posición corta
                    cost = tx.price * tx.quantity
                    cash_balance -= cost
                    position -= tx.quantity
                
                if position <= 0:
                    position = 0
                    avg_price = 0

            tx_index += 1

        # Obtener precio actual de las candles
        current_price = trade._get_price_at_time(df_candles, current_time)
        if current_price is None and avg_price > 0:
            current_price = avg_price

        # Calcular valor de la posición actual
        position_value = 0
        if position > 0 and current_price is not None:
            if trade.trade_type == 'LONG':
                # Para LONG: valor = precio_actual * cantidad
                position_value = current_price * position
            else:  # SHORT
                # Para SHORT: valor = (precio_entrada - precio_actual) * cantidad + precio_entrada * cantidad
                # Simplificado: valor = (2 * precio_entrada - precio_actual) * cantidad
                position_value = (2 * avg_price - current_price) * position

        # El balance total es el cash más el valor de la posición
        total_balance = cash_balance + position_value
        
        # PnL realizado es la diferencia entre cash actual e inicial (menos comisiones)
        realized_pnl = cash_balance - initial_balance
        
        # PnL no realizado es el valor de la posición menos lo que costó/se recibió originalmente
        unrealized_pnl = 0
        if position > 0 and current_price is not None:
            if trade.trade_type == 'LONG':
                unrealized_pnl = (current_price - avg_price) * position
            else:  # SHORT
                unrealized_pnl = (avg_price - current_price) * position

        # Guardar punto de la curva
        equity_points.append({
            'datetime': current_time.isoformat(),
            'date': current_time.date().isoformat(),
            'time': current_time.time().strftime('%H:%M:%S'),
            'balance': total_balance,
            'cash_balance': cash_balance,
            'position_value': position_value,
            'realized_pnl': realized_pnl,
            'unrealized_pnl': unrealized_pnl,
            'total_pnl': total_balance - initial_balance,
            'commission': commission_total,
            'position_size': position,
            'avg_price': avg_price,
            'current_price': current_price,
            'symbol': trade.symbol
        })

        current_time += timedelta(minutes=1)

    return equity_points

# TODO: Add all the candles needed for the charts of the trades already registered

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', 'trading_journal.db'))
engine = create_engine(f'sqlite:///{db_path}')
SessionMaker = sessionmaker(bind=engine)
session = SessionMaker()


trades: List[Trade] = session.query(Trade).all()

# TRACES 
equities = {trade.symbol + '_' + str(trade.id): {'data': pd.DataFrame(equity_curve(trade))['total_pnl'].to_list(), 'date': trade.entry_date} for trade in trades}
max_len = max(len(v['data']) for v in equities.values())
curves = pd.DataFrame({k: v['data'] + [np.nan]*(max_len - len(v['data'])) for k, v in equities.items()})


fig = px.line(curves, title='Trades Evolutions')
fig.show()

straight_up = []
straight_dn = []
finish_up = []
finish_dn = []
for c in curves.columns:
    min_idx = curves[c].idxmin()
    max_idx = curves[c].idxmax()
    entry = curves[c].iloc[0]
    if min_idx < max_idx and curves[c].iloc[min_idx] < entry and entry < curves[c].iloc[max_idx]:
        finish_up.append({'symbol': c, 'date': equities[c]['date']})
    elif min_idx < max_idx and curves[c].iloc[min_idx] == entry and entry < curves[c].iloc[max_idx]:
        straight_up.append({'symbol': c, 'date': equities[c]['date']})
    elif max_idx < min_idx and curves[c].iloc[min_idx] < entry and entry < curves[c].iloc[max_idx]:
        finish_dn.append({'symbol': c, 'date': equities[c]['date']})
    elif max_idx < min_idx and curves[c].iloc[max_idx] == entry and entry > curves[c].iloc[min_idx]:
        straight_dn.append({'symbol': c, 'date': equities[c]['date']})


print('Straight Up: ', len(straight_up))
print('Straight Dn: ', len(straight_dn))
print('Finish Up: ', len(finish_up))
print('Finish Dn: ', len(finish_dn))

bar_data = {'straight_up':{}, 'straight_dn': {}, 'finish_up': {}, 'finish_dn': {}}
for s in straight_up:
    bar_data['straight_up'][s['date']] = 1 if s['date'] not in bar_data['straight_up'] else bar_data['straight_up'][s['date']] + 1
for s in straight_dn:
    bar_data['straight_dn'][s['date']] = 1 if s['date'] not in bar_data['straight_dn'] else bar_data['straight_dn'][s['date']] + 1
for s in finish_up:
    bar_data['finish_up'][s['date']] = 1 if s['date'] not in bar_data['finish_up'] else bar_data['finish_up'][s['date']] + 1
for s in finish_dn:
    bar_data['finish_dn'][s['date']] = 1 if s['date'] not in bar_data['finish_dn'] else bar_data['finish_dn'][s['date']] + 1

bar_df = pd.DataFrame(bar_data).fillna(0).sort_index().rolling(5).sum()
fig = px.line(bar_df, title="Entry Timing Abs")
fig.show()

fig = px.line(bar_df.div(bar_df.sum(axis=1), axis=0) * 100, title="Entry Timing Pct")
fig.show()



# Get basic metrics of traded days.
for trade in trades:

    start_dt = datetime.combine(trade.entry_date, time(0, 0, 0, 0, tzinfo=timezone.utc))
    end_dt = start_dt + timedelta(days=1)

    trade.day_candles = session.query(Candle).filter(
        Candle.timeframe == '1m',
        Candle.symbol == trade.symbol,
        Candle.date >= start_dt,
        Candle.date < end_dt
    ).all()

def time_to_minutes(t):
    return t.hour * 60 + t.minute + t.second / 60

def minutes_to_time(minutes):
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return time(hours, mins)

min_times = []
max_times = []
hourly_trends = []
red_days = []
green_days = []
break_min_count = 0
break_max_count = 0
total_days = 0

for trade in trades:

    df = pd.DataFrame([c.to_dict() for c in trade.day_candles])
    
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    # Solo sesión regular
    regular = df[df['session'] == 'REGULAR']
    if regular.empty:
        continue
    total_days += 1

    # Hora del mínimo y máximo
    min_idx = regular['low'].idxmin()
    max_idx = regular['high'].idxmax()
    min_time = regular.loc[min_idx, 'date'].time()
    max_time = regular.loc[max_idx, 'date'].time()
    min_times.append(min_time)
    max_times.append(max_time)

    # Tendencia por hora
    regular['hour'] = regular['date'].dt.hour
    hourly = regular.groupby('hour').agg({'close': ['first', 'last']})
    hourly['trend'] = hourly['close']['last'] - hourly['close']['first']
    for hour, row in hourly.iterrows():
        hourly_trends.append({'hour': hour, 'trend': row['trend']})

    # ¿Se rompe el mínimo/máximo diario?
    day_min = regular['low'].cummin()
    day_max = regular['high'].cummax()
    break_min_count = sum(np.where(day_min < day_min.shift(1), 1, 0))
    break_max_count = sum(np.where(day_max > day_max.shift(1), 1, 0))

    if regular['open'].iloc[0] > regular['close'].iloc[-1]: red_days.append(regular['open'].iloc[0] - regular['close'].iloc[-1])
    elif regular['close'].iloc[-1] > regular['open'].iloc[0]: green_days.append(regular['close'].iloc[-1] - regular['open'].iloc[0])

# Estadísticas de hora de mínimos y máximos
min_times_series = pd.Series(min_times)
max_times_series = pd.Series(max_times)

min_minutes = min_times_series.apply(time_to_minutes)
max_minutes = max_times_series.apply(time_to_minutes)

print("Hora media del mínimo:", pd.to_datetime(min_minutes.mean(), unit='m').time(), "±", min_minutes.std(), ' minutos')
print("Hora media del máximo:", pd.to_datetime(max_minutes.mean(), unit='m').time(), "±", max_minutes.std(), ' minutos')

# Tendencia media por hora
hourly_trends_df = pd.DataFrame(hourly_trends)
mean_trend_by_hour = hourly_trends_df.groupby('hour')['trend'].mean()
print("Tendencia media por hora:")
print(mean_trend_by_hour)

# Probabilidad de romper mínimo/máximo diario al cierre
print("Media de rupturas de mínimos diarias:", break_min_count / total_days)
print("Media de rupturas de máximos diarias:", break_max_count / total_days)
print("Probabilidad de día alcista:", len(red_days) / total_days, (len(red_days) / total_days * sum(red_days)/len(red_days)) - (len(green_days) / total_days * sum(green_days)/len(green_days)) )
print("Probabilidad de día bajista:", len(green_days) / total_days, (len(green_days) / total_days * sum(green_days)/len(green_days)) - (len(red_days) / total_days * sum(red_days)/len(red_days)) )































import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, time, timedelta, timezone
from collections import defaultdict

def analyze_trades_by_performance(trades:list[Trade], session:Session) -> dict[str, dict]:
    """Analiza trades separados por ganadores y perdedores"""
    
    # Separar trades ganadores y perdedores
    winning_trades = [t for t in trades if hasattr(t, 'pnl') and t.profit_loss > 0]
    losing_trades = [t for t in trades if hasattr(t, 'pnl') and t.profit_loss <= 0]
    
    # Si no tienes campo pnl, usar otro criterio
    if not winning_trades and not losing_trades:
        # Ejemplo usando precio de entrada vs salida (ajustar según tu lógica)
        winning_trades = [t for t in trades if hasattr(t, 'exit_price') and t.exit_price > t.entry_price]
        losing_trades = [t for t in trades if hasattr(t, 'exit_price') and t.exit_price < t.entry_price]
    
    results = {}
    
    for category, trade_list in [("Ganadores", winning_trades), ("Perdedores", losing_trades), ("Todos", trades)]:
        if not trade_list:
            continue
            
        # Obtener datos de velas para estos trades
        for trade in trade_list:
            if not hasattr(trade, 'day_candles'):
                start_dt = datetime.combine(trade.entry_date, time(0, 0, 0, 0, tzinfo=timezone.utc))
                end_dt = start_dt + timedelta(days=1)
                trade.day_candles = session.query(Candle).filter(
                    Candle.timeframe == '1m',
                    Candle.symbol == trade.symbol,
                    Candle.date >= start_dt,
                    Candle.date < end_dt
                ).all()
        
        stats = calculate_statistics(trade_list)
        results[category] = stats
    
    return results

def calculate_statistics(trades:list[Trade]) -> dict:
    """Calcula estadísticas para una lista de trades"""
    
    min_times = []
    max_times = []
    hourly_trends = defaultdict(list)
    hourly_min_prob = defaultdict(int)  # Probabilidad de mínimo por hora
    hourly_max_prob = defaultdict(int)  # Probabilidad de máximo por hora
    red_days = []
    green_days = []
    break_min_count = 0
    break_max_count = 0
    total_days = 0
    hourly_returns = defaultdict(list)  # Retornos por hora
    
    # Para el heatmap 2D: hora + precio
    min_hour_price = []  # [(hora, precio_relativo)]
    max_hour_price = []  # [(hora, precio_relativo)]
    
    for trade in trades:
        df = pd.DataFrame([c.to_dict() for c in trade.day_candles])
        
        if df.empty:
            continue
            
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Solo sesión regular
        regular = df[df['session'] == 'REGULAR']
        if regular.empty:
            continue
            
        total_days += 1
        
        # Precio de apertura para calcular rendimientos
        day_open = regular['open'].iloc[0]
        
        # Hora y precio del mínimo y máximo
        min_idx = regular['low'].idxmin()
        max_idx = regular['high'].idxmax()
        min_time = regular.loc[min_idx, 'date'].time()
        max_time = regular.loc[max_idx, 'date'].time()
        min_price = regular.loc[min_idx, 'low']
        max_price = regular.loc[max_idx, 'high']
        
        min_times.append(min_time)
        max_times.append(max_time)
        
        # Calcular rendimiento desde apertura (en porcentaje)
        min_return = ((min_price - day_open) / day_open) * 100
        max_return = ((max_price - day_open) / day_open) * 100
        
        # Guardar hora y rendimiento desde apertura
        min_hour_price.append((regular.loc[min_idx, 'date'].hour, min_return))
        max_hour_price.append((regular.loc[max_idx, 'date'].hour, max_return))
        
        # Contar probabilidades por hora (mantener compatibilidad)
        min_hour = regular.loc[min_idx, 'date'].hour
        max_hour = regular.loc[max_idx, 'date'].hour
        hourly_min_prob[min_hour] += 1
        hourly_max_prob[max_hour] += 1
        
        # Retornos por hora
        regular['hour'] = regular['date'].dt.hour
        regular['returns'] = regular['close'].pct_change()
        
        for hour in range(24):
            hour_data = regular[regular['hour'] == hour]
            if not hour_data.empty:
                hour_return = (hour_data['close'].iloc[-1] - hour_data['open'].iloc[0]) / hour_data['open'].iloc[0]
                hourly_returns[hour].append(hour_return)
        
        # Tendencia por hora (para mantener compatibilidad)
        hourly = regular.groupby('hour').agg({'close': ['first', 'last']})
        hourly['trend'] = hourly['close']['last'] - hourly['close']['first']
        for hour, row in hourly.iterrows():
            hourly_trends[hour].append(row['trend'])
        
        # Rupturas de mínimo/máximo
        day_min = regular['low'].cummin()
        day_max = regular['high'].cummax()
        breaks_min = sum(np.where(day_min < day_min.shift(1), 1, 0))
        breaks_max = sum(np.where(day_max > day_max.shift(1), 1, 0))
        break_min_count += breaks_min
        break_max_count += breaks_max
        
        # Días rojos y verdes
        if regular['open'].iloc[0] > regular['close'].iloc[-1]:
            red_days.append(regular['open'].iloc[0] - regular['close'].iloc[-1])
        elif regular['close'].iloc[-1] > regular['open'].iloc[0]:
            green_days.append(regular['close'].iloc[-1] - regular['open'].iloc[0])
    
    # Convertir probabilidades a porcentajes
    for hour in hourly_min_prob:
        hourly_min_prob[hour] = hourly_min_prob[hour] / total_days * 100
    for hour in hourly_max_prob:
        hourly_max_prob[hour] = hourly_max_prob[hour] / total_days * 100
    
    return {
        'min_times': min_times,
        'max_times': max_times,
        'min_hour_price': min_hour_price,  # Nuevo: datos para heatmap 2D
        'max_hour_price': max_hour_price,  # Nuevo: datos para heatmap 2D
        'hourly_trends': hourly_trends,
        'hourly_min_prob': dict(hourly_min_prob),
        'hourly_max_prob': dict(hourly_max_prob),
        'hourly_returns': dict(hourly_returns),
        'red_days': red_days,
        'green_days': green_days,
        'break_min_count': break_min_count,
        'break_max_count': break_max_count,
        'total_days': total_days
    }

def create_heatmap_visualization(results:dict[str, dict]):
    """Crea visualización interactiva con Plotly - Heatmap 2D (Hora + Precio)"""
    
    categories = ['Ganadores', 'Perdedores'] if 'Ganadores' in results and 'Perdedores' in results else ['Todos']
    
    # Solo 2 subplots: heatmap 2D arriba, barras abajo
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=['Mapa de Calor 2D: Probabilidad por Hora y Precio + Retornos Acumulados', 'Probabilidades por Hora'],
        specs=[[{"secondary_y": True}], [{"secondary_y": False}]],
        vertical_spacing=0.15
    )
    
    hours = list(range(9, 21))  # Horario de mercado típico
    hour_labels = [f'{h:02d}:00' for h in hours]
    
    # Crear bins de precio (de 0 a 100% del rango diario)
    price_bins = list(range(0, 101, 10))  # 0%, 10%, 20%, ..., 100%
    price_labels = [f'{p}%' for p in price_bins]
    
    colors = ['blue', 'red', 'green']
    
    for idx, category in enumerate(categories):
        if category not in results:
            continue
            
        stats = results[category]
        color = colors[idx % len(colors)]
        
        # Preparar datos para barras (mantener compatibilidad)
        min_probs = [stats['hourly_min_prob'].get(hour, 0) for hour in hours]
        max_probs = [stats['hourly_max_prob'].get(hour, 0) for hour in hours]
        
        # Retornos acumulados
        cumulative_returns = []
        for hour in hours:
            hour_returns = stats['hourly_returns'].get(hour, [0])
            mean_return = np.mean(hour_returns) * 100
            cumulative_returns.append(mean_return)
        
        cumulative = np.cumsum(cumulative_returns)
        
        # Crear heatmap 2D solo para el primer dataset o todos si es uno solo
        if idx == 0 or len(categories) == 1:
            # Crear matriz de densidad 2D
            heatmap_matrix = np.zeros((len(price_bins)-1, len(hours)))
            
            # Procesar datos de mínimos (valores negativos para distinguir)
            for hour_val, price_val in stats['min_hour_price']:
                if hour_val in hours:
                    hour_idx = hours.index(hour_val)
                    price_idx = min(int(price_val / 10), len(price_bins)-2)  # Bin de precio
                    heatmap_matrix[price_idx, hour_idx] -= 1  # Negativo para mínimos
            
            # Procesar datos de máximos (valores positivos)
            for hour_val, price_val in stats['max_hour_price']:
                if hour_val in hours:
                    hour_idx = hours.index(hour_val)
                    price_idx = min(int(price_val / 10), len(price_bins)-2)  # Bin de precio
                    heatmap_matrix[price_idx, hour_idx] += 1  # Positivo para máximos
            
            # Invertir matriz para que 0% esté abajo y 100% arriba
            heatmap_matrix = np.flipud(heatmap_matrix)
            price_labels_flipped = list(reversed(price_labels[:-1]))
            
            # Heatmap 2D
            fig.add_trace(
                go.Heatmap(
                    z=heatmap_matrix,
                    x=hour_labels,
                    y=price_labels_flipped,
                    colorscale='RdYlGn',
                    zmid=0,  # Centro en 0
                    opacity=0.8,
                    showscale=True,
                    colorbar=dict(
                        title="Densidad<br>Máx (+) / Mín (-)",
                        x=1.02,
                        len=0.4,
                        y=0.75
                    ),
                    hovertemplate='Hora: %{x}<br>Precio: %{y}<br>Densidad: %{z}<extra></extra>',
                    name='Densidad 2D'
                ),
                row=1, col=1
            )
        
        # Línea de retornos acumulados superpuesta
        fig.add_trace(
            go.Scatter(
                x=hour_labels,
                y=cumulative,
                mode='lines+markers',
                line=dict(color=color, width=4),
                marker=dict(size=10, symbol='diamond'),
                name=f'Retorno Acumulado - {category}',
                yaxis='y2',
                hovertemplate='Hora: %{x}<br>Retorno Acum: %{y:.2f}%<extra></extra>',
                opacity=0.9
            ),
            row=1, col=1, secondary_y=True
        )
        
        # Barras de probabilidades por hora
        fig.add_trace(
            go.Bar(
                x=hour_labels,
                y=min_probs,
                name=f'Prob. Mínimo - {category}',
                marker_color=f'rgba({255 if idx==0 else 255-idx*50}, {99 if idx==0 else 99+idx*30}, {71 if idx==0 else 71+idx*20}, 0.7)',
                hovertemplate='Hora: %{x}<br>Prob. Mínimo: %{y:.1f}%<extra></extra>',
                offsetgroup=f'min_{idx}'
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=hour_labels,
                y=max_probs,
                name=f'Prob. Máximo - {category}',
                marker_color=f'rgba({50 if idx==0 else 50+idx*30}, {205 if idx==0 else 205-idx*30}, {50 if idx==0 else 50+idx*30}, 0.7)',
                hovertemplate='Hora: %{x}<br>Prob. Máximo: %{y:.1f}%<extra></extra>',
                offsetgroup=f'max_{idx}'
            ),
            row=2, col=1
        )
    
    # Layout
    fig.update_layout(
        height=900,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template='plotly_white'
    )
    
    # Configurar ejes
    fig.update_yaxes(
        title_text="Rendimiento vs Apertura (%)",
        row=1, col=1
    )
    
    fig.update_yaxes(
        title_text="Retorno Acumulado (%)",
        title_font_color="blue",
        tickfont_color="blue",
        row=1, col=1, secondary_y=True
    )
    
    fig.update_yaxes(
        title_text="Probabilidad (%)",
        row=2, col=1
    )
    
    fig.update_xaxes(
        title_text="Hora del Día",
        row=2, col=1
    )
    
    fig.update_xaxes(
        title_text="Hora del Día",
        row=1, col=1
    )
    
    fig.show()
    return fig
def create_probabilistic_scatter_fixed(results):
    """
    Scatter 2D de mínimos/máximos con tamaño según probabilidad
    + Curva de retorno acumulado medio sobre el mismo eje.
    """
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    from collections import defaultdict
    
    min_counter = defaultdict(int)
    max_counter = defaultdict(int)
    cumulative_series = defaultdict(list)
    
    total_days = max([stats['total_days'] for stats in results.values()] + [1])
    
    # Recorremos cada trade/category
    for stats in results.values():
        for h, r in stats['min_hour_price']:
            r_rounded = round(r, 1)
            min_counter[(h, r_rounded)] += 1
        for h, r in stats['max_hour_price']:
            r_rounded = round(r, 1)
            max_counter[(h, r_rounded)] += 1
        # Retorno acumulado medio: guardamos todos los retornos por hora
        for h, returns in stats['hourly_returns'].items():
            cumulative_series[h].extend([ret*100 for ret in returns])
    
    # Preparar scatter
    def prepare_scatter(counter, color, name):
        xs, ys, sizes = [], [], []
        for (h, r), count in counter.items():
            prob = count / total_days
            if prob > 0:
                xs.append(h)
                ys.append(r)
                sizes.append(prob*30)  # Escalar tamaño visual
        return go.Scatter(
            x=xs, y=ys, mode='markers',
            marker=dict(size=sizes, color=color, opacity=0.6),
            name=name,
            hovertemplate='Hora: %{x}:00<br>Retorno: %{y:.1f}%<br>Prob: %{marker.size:.1f}<extra></extra>'
        )
    
    fig = go.Figure()
    fig.add_trace(prepare_scatter(min_counter, 'red', 'Mínimos'))
    fig.add_trace(prepare_scatter(max_counter, 'green', 'Máximos'))
    
    # Curva de retorno acumulado medio
    hours_sorted = sorted(cumulative_series.keys())
    mean_returns = []
    for h in hours_sorted:
        mean_returns.append(np.mean(cumulative_series[h]))
    mean_cum = np.cumsum(mean_returns)
    
    fig.add_trace(go.Scatter(
        x=hours_sorted,
        y=mean_cum,
        mode='lines+markers',
        line=dict(color='blue', width=3),
        marker=dict(size=6, symbol='diamond'),
        name='Retorno Acumulado Medio',
        hovertemplate='Hora: %{x}:00<br>Retorno Acum Medio: %{y:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title='Scatter Probabilístico de Mínimos/Máximos + Retorno Medio Acumulado',
        xaxis_title='Hora del Día',
        yaxis_title='Retorno vs Apertura (%)',
        template='plotly_white',
        height=700,
        showlegend=True
    )
    
    fig.show()
    return fig

def create_summary_dashboard(results):
    """Crea un dashboard resumen adicional"""
    
    categories = list(results.keys())
    
    # Crear subplot para métricas resumen
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            'Distribución Horaria de Mínimos',
            'Distribución Horaria de Máximos', 
            'Retorno Medio por Hora',
            'Comparación de Métricas'
        ],
        specs=[[{"type": "polar"}, {"type": "polar"}],
               [{"type": "xy"}, {"type": "xy"}]]
    )
    
    colors = ['blue', 'red', 'green']
    
    for idx, category in enumerate(categories):
        stats = results[category]
        color = colors[idx % len(colors)]
        
        # 1. Distribución polar de mínimos
        min_hours = [t.hour for t in stats['min_times']]
        min_counts = pd.Series(min_hours).value_counts().sort_index()
        
        fig.add_trace(
            go.Scatterpolar(
                r=min_counts.values,
                theta=[f'{h}:00' for h in min_counts.index],
                fill='toself',
                name=f'Mínimos - {category}',
                marker_color=color,
                opacity=0.6
            ),
            row=1, col=1
        )
        
        # 2. Distribución polar de máximos
        max_hours = [t.hour for t in stats['max_times']]
        max_counts = pd.Series(max_hours).value_counts().sort_index()
        
        fig.add_trace(
            go.Scatterpolar(
                r=max_counts.values,
                theta=[f'{h}:00' for h in max_counts.index],
                fill='toself',
                name=f'Máximos - {category}',
                marker_color=color,
                opacity=0.6,
                line_dash='dash'
            ),
            row=1, col=2
        )
        
        # 3. Retorno medio por hora
        hours = sorted(stats['hourly_returns'].keys())
        returns = [np.mean(stats['hourly_returns'][h]) * 100 for h in hours]
        
        fig.add_trace(
            go.Scatter(
                x=[f'{h:02d}:00' for h in hours],
                y=returns,
                mode='lines+markers',
                name=f'Retorno - {category}',
                line=dict(color=color, width=2),
                marker=dict(size=6)
            ),
            row=2, col=1
        )
    
    # 4. Comparación de métricas clave
    if len(categories) > 1:
        metrics = []
        values = []
        cats = []
        
        for category in categories:
            stats = results[category]
            
            # Calcular métricas
            avg_breaks_min = stats['break_min_count'] / max(stats['total_days'], 1)
            avg_breaks_max = stats['break_max_count'] / max(stats['total_days'], 1)
            prob_green = len(stats['green_days']) / max(stats['total_days'], 1) * 100
            prob_red = len(stats['red_days']) / max(stats['total_days'], 1) * 100
            
            metrics.extend(['Rupturas Mín', 'Rupturas Máx', 'Días Alcistas (%)', 'Días Bajistas (%)'])
            values.extend([avg_breaks_min, avg_breaks_max, prob_green, prob_red])
            cats.extend([category] * 4)
        
        df_metrics = pd.DataFrame({
            'Métrica': metrics,
            'Valor': values,
            'Categoría': cats
        })
        
        for category in categories:
            df_cat = df_metrics[df_metrics['Categoría'] == category]
            fig.add_trace(
                go.Bar(
                    x=df_cat['Métrica'],
                    y=df_cat['Valor'],
                    name=category,
                    marker_color=colors[categories.index(category)]
                ),
                row=2, col=2
            )
    
    fig.update_layout(
        title='Dashboard Resumen de Trading',
        height=800,
        showlegend=True
    )
    
    fig.show()
    
    return fig

def print_statistics(results):
    """Imprime estadísticas resumidas"""
    
    for category, stats in results.items():
        print(f"\n{'='*50}")
        print(f"ESTADÍSTICAS - {category.upper()}")
        print(f"{'='*50}")
        print(f"Total de días analizados: {stats['total_days']}")
        
        # Horas promedio de mínimos y máximos
        if stats['min_times']:
            min_minutes = pd.Series(stats['min_times']).apply(time_to_minutes)
            max_minutes = pd.Series(stats['max_times']).apply(time_to_minutes)
            
            avg_min_time = minutes_to_time(min_minutes.mean())
            avg_max_time = minutes_to_time(max_minutes.mean())
            
            print(f"Hora media del mínimo: {avg_min_time} (±{min_minutes.std():.1f} min)")
            print(f"Hora media del máximo: {avg_max_time} (±{max_minutes.std():.1f} min)")
        
        # Rupturas
        if stats['total_days'] > 0:
            print(f"Media de rupturas de mínimos: {stats['break_min_count']/stats['total_days']:.2f}")
            print(f"Media de rupturas de máximos: {stats['break_max_count']/stats['total_days']:.2f}")
            
            # Días alcistas vs bajistas
            total_red = len(stats['red_days'])
            total_green = len(stats['green_days'])
            total_days = stats['total_days']
            
            prob_red = total_red / total_days
            prob_green = total_green / total_days
            
            print(f"Probabilidad de día bajista: {prob_red:.2%}")
            print(f"Probabilidad de día alcista: {prob_green:.2%}")
        
        # Top 3 horas con mayor probabilidad de mínimo/máximo
        if stats['hourly_min_prob']:
            top_min_hours = sorted(stats['hourly_min_prob'].items(), key=lambda x: x[1], reverse=True)[:3]
            top_max_hours = sorted(stats['hourly_max_prob'].items(), key=lambda x: x[1], reverse=True)[:3]
            
            print("\nTop 3 horas con mayor probabilidad de mínimo:")
            for hour, prob in top_min_hours:
                print(f"  {hour:02d}:00 - {prob:.1f}%")
            
            print("\nTop 3 horas con mayor probabilidad de máximo:")
            for hour, prob in top_max_hours:
                print(f"  {hour:02d}:00 - {prob:.1f}%")

# Analizar por categorías
results = analyze_trades_by_performance(trades, session)

# Mostrar estadísticas
print_statistics(results)

# Crear visualizaciones interactivas
heatmap_fig = create_heatmap_visualization(results)
# summary_fig = create_summary_dashboard(results)
