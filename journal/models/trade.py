
from datetime import datetime, timezone
from sqlalchemy import and_

from .base import Model, db
from .error import Error, trade_errors
from .transaction import Transaction
from .strategy_condition import StrategyCondition

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
        
    def to_dict(self, exclude:list=[]):
        return {
            'id': self.id,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'exit_date': self.exit_date.isoformat() if self.exit_date else None,
            'symbol': self.symbol,
            'company_name': self.company_name,
            'entry_price': self.entry_price,
            'entry_time': self.entry_time,
            'exit_price': self.exit_price,
            'exit_time': self.exit_time,
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
            'created_at': self.created_at.isoformat() if self.created_at else None
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
    
    @property
    def error_descriptions(self):
        """Lista de descripciones de errores para este trade"""
        return [error.description for error in self.errors]