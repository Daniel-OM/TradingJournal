
from datetime import date, datetime, timezone

from .base import Model, db

# Tabla de asociación para la relación muchos a muchos entre Trade y Error
trade_errors = db.Table('trade_error',
    db.Column('trade_id', db.Integer, db.ForeignKey('trade.id'), primary_key=True),
    db.Column('error_id', db.Integer, db.ForeignKey('error.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.now(timezone.utc)),
    db.Column('impact_level', db.String(10), default='medium')  # low, medium, high
)

class Error(Model):
    __tablename__ = 'error'
    
    description = db.Column(db.String(500), nullable=False, unique=True)
    category = db.Column(db.String(100))  # 'psychological', 'technical', 'risk_management', 'execution'
    severity = db.Column(db.String(10), default='medium')  # low, medium, high
    is_active = db.Column(db.Boolean, default=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='errors')
    
    # Relación muchos a muchos con Trade
    trades = db.relationship('Trade', secondary=trade_errors, back_populates='errors')
    
    def to_dict(self, exclude:list=[]):
        return {
            'id': self.id,
            'description': self.description,
            'category': self.category,
            'severity': self.severity,
            'is_active': self.is_active,
            'trades': [] if 'trades' in exclude else [t.to_dict(exclude=['errors']+exclude) for t in self.trades],
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    @property
    def occurrence_count(self):
        """Cuenta cuántas veces ha ocurrido este error"""
        return len(self.trades)
    
    @property
    def last_occurrence(self):
        """Fecha de la última ocurrencia del error"""
        if not self.trades:
            return None
        return max(trade.entry_date for trade in self.trades)
    
    @property
    def days_since_last_occurrence(self):
        """Días desde la última ocurrencia"""
        last_date = self.last_occurrence
        if not last_date:
            return None
        return (date.today() - last_date).days
    
    @property
    def recent_examples(self):
        """Últimos 5 trades con este error"""
        return sorted(self.trades, key=lambda t: t.entry_date, reverse=True)[:5]
    
    @property
    def average_impact(self):
        """Impacto promedio en P&L de este error"""
        if not self.trades:
            return 0
        total_loss = sum(trade.profit_loss for trade in self.trades if trade.profit_loss < 0)
        return total_loss / len(self.trades) if self.trades else 0
    
    def __repr__(self):
        return f'<Error {self.description}>'
