"""
Schemas para Candle
"""

from pydantic import BaseModel
from datetime import datetime


class CandleBase(BaseModel):
    symbol: str
    date: datetime
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class CandleCreate(CandleBase):
    pass


class CandleResponse(CandleBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
