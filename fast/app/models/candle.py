"""
Modelo Candle
"""

from sqlalchemy import Column, String, Integer, Float, DateTime
from datetime import datetime, timezone
from app.db.database import BaseModel


class Candle(BaseModel):
    """Datos OHLCV de velas"""
    __tablename__ = "candles"
        
    # Identificadores
    symbol = Column(String(20), index=True)
    date = Column(DateTime, index=True)
    timeframe = Column(String(10))  # 1m, 5m, 1h, 1d, etc
    
    # OHLCV
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    session = Column(String(10), default='REG') # PRE, REG, POST
