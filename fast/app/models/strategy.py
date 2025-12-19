"""
Modelos Strategy y StrategyCondition
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Float, Text, Table
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base

# Association table for trades and strategy conditions
trade_scoring = Table(
    'trade_scoring',
    Base.metadata,
    Column('trade_id', Integer, ForeignKey('trades.id'), primary_key=True),
    Column('strategy_condition_id', Integer, ForeignKey('strategy_conditions.id'), primary_key=True)
)


class Strategy(Base):
    """Estrategias de trading"""
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    name = Column(String(255), index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relaciones
    user = relationship("User", back_populates="strategies")
    trades = relationship("Trade", back_populates="strategy")
    conditions = relationship("StrategyCondition", back_populates="strategy", cascade="all, delete-orphan")


class StrategyCondition(Base):
    """Condiciones dentro de una estrategia"""
    __tablename__ = "strategy_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey('strategies.id'), index=True)
    name = Column(String(255))
    description = Column(Text, nullable=True)
    score = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relaciones
    strategy = relationship("Strategy", back_populates="conditions")
    trades = relationship(
        "Trade",
        secondary=trade_scoring,
        back_populates="conditions"
    )
    
    # Relaciones
    strategy = relationship("Strategy", back_populates="conditions")
