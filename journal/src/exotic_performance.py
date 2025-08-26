import pytz
from datetime import date, time, datetime, timedelta, timezone
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
Session = sessionmaker(bind=engine)
session = Session()


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
