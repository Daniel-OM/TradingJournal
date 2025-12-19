"""
Modelo Transaction
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base


class Transaction(Base):
    """Detalles de ejecución de trades"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, ForeignKey('trades.id'), index=True)
    
    # Información de ejecución
    date = Column(DateTime, index=True)
    time = Column(String(10), nullable=True)
    price = Column(Float)
    quantity = Column(Integer)
    transaction_type = Column(String(20))  # BUY, SELL
    
    # Costos
    commission = Column(Float, nullable=True)
    ecn_fee = Column(Float, nullable=True)
    locates = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relaciones
    trade = relationship("Trade", back_populates="transactions")
