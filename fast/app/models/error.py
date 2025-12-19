"""
Modelo Error
"""
from datetime import date

from sqlalchemy import Column, String, Integer, Table, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import BaseModel

# Tabla de asociación para Trade-Error
trade_errors = Table(
    'trade_errors',
    BaseModel.metadata,
    Column('trade_id', Integer, ForeignKey('trades.id'), primary_key=True),
    Column('error_id', Integer, ForeignKey('errors.id'), primary_key=True),
    Column('impact_level', String(50), nullable=True, default='medium'),  # low, medium, high
    Column('created_at', DateTime, default=datetime.now(timezone.utc)),
)

class Error(BaseModel):
    """Registro de errores y excepciones"""
    __tablename__ = "errors"
    
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    
    # Información del error
    description = Column(Text)
    category = Column(String(50))  # technical, execution, analysis, etc
    severity = Column(String(20))  # low, medium, high, critical
    
    # Relaciones
    user = relationship("User", back_populates="errors")
    
    trades = relationship('Trade', secondary=trade_errors, back_populates='errors')
    
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
