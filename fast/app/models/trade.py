"""
Modelo Trade
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Table
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


class Trade(Base):
    """Transacciones comerciales (trades)"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    symbol = Column(String(20), index=True)
    
    # Entrada
    entry_date = Column(DateTime, index=True)
    entry_price = Column(Float)
    entry_time = Column(String(10), nullable=True)
    
    # Salida
    exit_date = Column(DateTime, nullable=True, index=True)
    exit_price = Column(Float, nullable=True)
    exit_time = Column(String(10), nullable=True)
    
    # Cantidad y tipo
    quantity = Column(Integer)
    exit_quantity = Column(Integer, nullable=True)
    trade_type = Column(String(20))  # LONG, SHORT
    
    # Financiero
    profit_loss = Column(Float, nullable=True)
    commission = Column(Float, default=0)
    balance = Column(Float, nullable=True)
    
    # Metadata
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=True)
    description = Column(Text, nullable=True)
    hashtags = Column(String(500), nullable=True)
    
    # Stop y target
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relaciones
    user = relationship("User", back_populates="trades")
    strategy = relationship("Strategy", back_populates="trades")
    conditions = relationship(
        "StrategyCondition",
        secondary=trade_scoring,
        back_populates="trades"
    )
    transactions = relationship("Transaction", back_populates="trade", cascade="all, delete-orphan")
    media = relationship("Media", back_populates="trade", cascade="all, delete-orphan")

