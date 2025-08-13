
from datetime import datetime, timedelta, timezone
import pandas as pd
from sqlalchemy import and_

from .base import Model, db
from .error import Error, trade_errors
from .transaction import Transaction
from .strategy_condition import StrategyCondition
from .candle import Candle

# Tabla de asociación para la relación muchos a muchos entre Watchlist y Level
trade_scoring = db.Table('trade_scoring',
    db.Column('trade_id', db.Integer, db.ForeignKey('trade.id'), primary_key=True),
    db.Column('scoring_id', db.Integer, db.ForeignKey('strategy_condition.id'), primary_key=True),
    db.Column('value', db.Float, default=0.0),
    db.Column('created_at', db.DateTime, default=datetime.now(timezone.utc))
)

class Trade(Model):
    __tablename__ = 'trade'

    entry_date = db.Column(db.Date)
    exit_date = db.Column(db.Date)
    symbol = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(200))
    entry_price = db.Column(db.Float)
    entry_time = db.Column(db.String(10))
    exit_price = db.Column(db.Float)
    exit_time = db.Column(db.String(10))
    stop_loss = db.Column(db.Float)
    take_profit = db.Column(db.Float)
    quantity = db.Column(db.Float)
    exit_quantity = db.Column(db.Float)
    balance = db.Column(db.Float)
    commission = db.Column(db.Float)
    trade_type = db.Column(db.String(10), default='LONG')  # LONG/SHORT
    description = db.Column(db.Text)
    why_profitable = db.Column(db.Text)
    influencing_factors = db.Column(db.Text)
    profit_loss = db.Column(db.Float, default=0)
    hashtags = db.Column(db.String(500)) # TODO: Define table for hashtags?
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'))
    
    strategy = db.relationship('Strategy', back_populates='trades')
    errors = db.relationship('Error', secondary='trade_error', back_populates='trades')
    conditions = db.relationship('StrategyCondition', secondary='trade_scoring', back_populates='trades')
    media = db.relationship('Media', back_populates='trade', cascade='all, delete-orphan', lazy='dynamic')
    transactions = db.relationship('Transaction', back_populates='trade', cascade='all, delete-orphan', lazy='dynamic')
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='trades')

    def __init__(self, **kwargs):
        # Convertir cadenas vacías a None para campos float
        float_fields: list[str] = ['entry_price', 'exit_price', 'stop_loss', 'take_profit', 
                       'quantity', 'exit_quantity', 'balance', 'commission', 'profit_loss']
        
        for field in float_fields:
            if field in kwargs and kwargs[field] == '':
                kwargs[field] = None
        
        super().__init__(**kwargs)
        
    def to_dict(self, exclude:list=[], equity:bool=False):
        return {
            'id': self.id,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'exit_date': self.exit_date.isoformat() if self.exit_date else None,
            'symbol': self.symbol,
            'company_name': self.company_name,
            'entry_price': self.entry_price,
            'entry_time': self.entry_time + '+00:00',
            'exit_price': self.exit_price,
            'exit_time': self.exit_time + '+00:00',
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'quantity': self.quantity,
            'balance': self.balance,
            'commission': self.commission,
            'trade_type': self.trade_type,
            'description': self.description,
            'why_profitable': self.why_profitable,
            'influencing_factors': self.influencing_factors,
            'profit_loss': self.profit_loss,
            'hashtags': self.hashtags,
            'strategy_id': self.strategy_id,
            'strategy': {} if 'strategy' in exclude else self.strategy.to_dict(exclude=['trades']+exclude),
            'media': [] if 'media' in exclude else [m.to_dict(exclude=['trade']+exclude) for m in self.media],
            'errors': [] if 'errors' in exclude else [e.to_dict(exclude=['trades']+exclude) for e in self.errors],
            'conditions': [] if 'conditions' in exclude else [c.to_dict(exclude=['trades', 'strategy']+exclude) for c in self.conditions],
            'transactions': [] if 'transactions' in exclude else [c.to_dict(exclude=['trade']+exclude) for c in self.transactions],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'equity': self.equity_curve() if equity else [],
        }
    
    def add_transaction(self, date, price:float, time, quantity:float, commission:float, type:str):
        
        if self.entry_date is None:
            self.entry_date = date
            self.entry_time = time
        if self.commission is None:
            self.commission = 0.0
            
        self.commission += commission

        if type == self.trade_type:
            if self.quantity is None:
                self.quantity = 0.0
            if self.entry_price is None:
                self.entry_price = 0.0

            self.entry_price = (self.entry_price * self.quantity + price * quantity) / (self.quantity + quantity)
            self.quantity += quantity

            if self.exit_price is not None and self.exit_quantity is not None:
                self.profit_loss = (self.exit_price - self.entry_price) * (-1 if self.trade_type == 'SHORT' else 1) * self.exit_quantity - self.commission
        else:
            if self.exit_quantity is None:
                self.exit_quantity = 0.0
            if self.exit_price is None:
                self.exit_price = 0.0

            self.exit_price = (self.exit_price * self.exit_quantity + price * quantity) / (self.exit_quantity + quantity)
            self.exit_quantity += quantity
            self.profit_loss = (self.exit_price - self.entry_price) * (-1 if self.trade_type == 'SHORT' else 1) * self.exit_quantity - self.commission
        
        if self.quantity == self.exit_quantity:
            self.exit_date = date
            self.exit_time = time

        db.session.add(Transaction(date=date, price=price, time=time, commission=commission, quantity=quantity, type=type, trade_id=self.id))
        db.session.commit()

    def add_error(self, description, user_id:int=None, id=None, impact_level='medium', category='general'):
        """Agregar un error a este trade"""
        
        if user_id is None: user_id = self.user_id

        # Buscar o crear el error
        if id is None or id == '':
            error = Error.query.filter_by(description=description).first()
            if not error:
                error = Error(
                    description=description,
                    category=category,
                    severity=self._determine_severity(impact_level.lower()),
                    user_id=user_id
                )
                db.session.add(error)
                db.session.flush([error])
        else:
            error = Error.query.filter_by(id=id).first()
        
        # Verificar si la relación ya existe
        errors = db.session.execute(
            trade_errors.select().where(
                and_(trade_errors.c.trade_id == self.id, 
                        trade_errors.c.error_id == error.id)
            )
        ).first()
        
        if not errors:
            db.session.execute(
                trade_errors.insert().values(
                    trade_id=self.id,
                    error_id=error.id,
                    impact_level=impact_level
                )
            )
        
        db.session.commit()
    
    def remove_error(self, error_description):
        """Remover un error de este trade"""
        error = Error.query.filter_by(description=error_description).first()
        if error and error in self.errors:
            self.errors.remove(error)
    
    def remove_errors(self):
        """Remover un level de este trade"""
        for error in self.errors:
            db.session.execute(
                trade_errors.delete().where(and_(trade_errors.c.error_id == error.id, trade_errors.c.trade_id == self.id))
            )
            
        db.session.commit()
    
    def _determine_severity(self, impact_level):
        """Determinar severidad basada en el nivel de impacto"""
        mapping = {
            'low': 'low',
            'medium': 'medium', 
            'high': 'high'
        }
        return mapping.get(impact_level, 'medium')
    
    def add_condition(self, condition_id:int, value:float):
        if condition_id is None or condition_id == '':
            return
        
        condition = StrategyCondition.query.filter_by(id=condition_id).first()
        
        # Verificar si la relación ya existe
        exists = db.session.execute(
            trade_scoring.select().where(
                (trade_scoring.c.trade_id == self.id) &
                (trade_scoring.c.scoring_id == condition_id)
            )
        ).first()
        if not exists:
            db.session.execute(
                trade_scoring.insert().values(
                    trade_id=self.id,
                    scoring_id=condition_id,
                    value=float(value),
                )
            )

        db.session.commit()

    def remove_conditions(self):
        for condition in self.conditions:
            db.session.execute(
                trade_scoring.delete().where(and_(trade_scoring.c.scoring_id == condition.id, trade_scoring.c.trade_id == self.id))
            )
        
        db.session.commit()

    def getCandles(self, timeframe='1m') -> list[Candle]:
        
        start_datetime = datetime.combine(self.entry_date, datetime.strptime(self.entry_time, '%H:%M:%S').time())
        end_datetime = datetime.combine(self.exit_date, datetime.strptime(self.exit_time, '%H:%M:%S').time())

        candles = Candle.query.filter(
            Candle.symbol == self.symbol,
            Candle.date >= start_datetime,
            Candle.date <= end_datetime,
            Candle.timeframe == timeframe
        ).all()

        if not candles:
            print(f'No candles data between {start_datetime} and {end_datetime}')
            return []
        
        return candles
    
    @property
    def error_descriptions(self):
        """Lista de descripciones de errores para este trade"""
        return [error.description for error in self.errors]
    
    def get_transaction_datetime(self, tx:Transaction) -> datetime:
        # Combinar fecha (date) con hora UTC (time)
        time_str = tx.time or '00:00:00'
        # Asegurar que tenga formato HH:MM:SS
        if len(time_str.split(':')) == 2:
            time_str += ':00'
        
        naive_dt = datetime.combine(tx.date, datetime.strptime(time_str, '%H:%M:%S').time())
        # Convertir a UTC ya que las horas están en UTC
        return naive_dt.replace(tzinfo=timezone.utc)
    
    def getStartEndDatetime(self) -> tuple[datetime, datetime, list[Transaction]]:

        sorted_transactions = sorted(self.transactions, key=self.get_transaction_datetime)

        # Obtener el rango de tiempo
        start_datetime = self.get_transaction_datetime(sorted_transactions[0]) - timedelta(minutes=1)
        end_datetime = self.get_transaction_datetime(sorted_transactions[-1]) + timedelta(minutes=1)

        return start_datetime, end_datetime, sorted_transactions
    
    def equity_curve(self, initial_balance: float = 0):
        if not self.transactions:
            return []

        start_datetime, end_datetime, sorted_transactions = self.getStartEndDatetime()

        # Buscar candles en el rango (date ya es datetime con UTC)
        candles = self.getCandles(timeframe='1m')

        # Preparar DataFrame de candles
        df_candles = pd.DataFrame([c.to_dict() for c in candles])
        # date ya es datetime UTC, solo necesitamos asegurar que es datetime
        df_candles['datetime'] = pd.to_datetime(df_candles['date'], utc=True)
        df_candles.set_index('datetime', inplace=True)
        df_candles.sort_index(inplace=True)

        # Crear lista de transacciones con datetime completo
        transactions_with_dt = []
        for tx in sorted_transactions:
            tx_dt = self.get_transaction_datetime(tx)
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

                if tx.type == self.trade_type:  # Transacción de entrada (compra para LONG, venta para SHORT)
                    if self.trade_type == 'LONG':
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
                    if self.trade_type == 'LONG':
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
            current_price = self._get_price_at_time(df_candles, current_time)
            if current_price is None and avg_price > 0:
                current_price = avg_price

            # Calcular valor de la posición actual
            position_value = 0
            if position > 0 and current_price is not None:
                if self.trade_type == 'LONG':
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
                if self.trade_type == 'LONG':
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
                'symbol': self.symbol
            })

            current_time += timedelta(minutes=1)

        return equity_points

    def _get_price_at_time(self, df_candles, target_time):
        """
        Obtiene el precio más cercano al tiempo objetivo.
        
        Args:
            df_candles (DataFrame): DataFrame con velas indexado por datetime UTC
            target_time (datetime): Tiempo objetivo en UTC
            
        Returns:
            float: Precio de cierre más cercano
        """
        if df_candles.empty:
            return None
        
        # Asegurar que target_time tiene timezone UTC
        if target_time.tzinfo is None:
            target_time = target_time.replace(tzinfo=timezone.utc)
        
        try:
            # Buscar el precio exacto
            if target_time in df_candles.index:
                return float(df_candles.loc[target_time, 'close'])
            
            # Buscar el precio más cercano (anterior)
            before = df_candles[df_candles.index <= target_time]
            if not before.empty:
                return float(before.iloc[-1]['close'])
            
            # Si no hay precios anteriores, usar el siguiente
            after = df_candles[df_candles.index > target_time]
            if not after.empty:
                return float(after.iloc[0]['close'])
                
        except Exception as e:
            print(f"Error getting price at time {target_time}: {e}")
            pass
        
        return None
    
    def maximumFavorableAverse(self) -> tuple[float, float]:
        
        if not self.transactions:
            return 0.0, 0.0
        
        # Obtener precios de entrada y salida
        entry_price = self.entry_price
        exit_price = self.exit_price
        candles: list[Candle] = self.getCandles(timeframe='1m')
        
        if entry_price is None or exit_price is None:
            return 0.0, 0.0
        
        mae = max(self.entry_price - candle.close for candle in candles if candle.date >= self.entry_date and candle.date <= self.exit_date)
        mfe = max(candle.close - self.entry_price for candle in candles if candle.date >= self.entry_date and candle.date <= self.exit_date)

        return mae, mfe