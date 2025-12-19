"""
Schemas para Transaction
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TransactionBase(BaseModel):
    date: datetime
    time: Optional[str] = None
    price: float
    quantity: float
    type: str  # BUY, SELL
    commission: float = 0
    ecn_fee: float = 0
    locates: float = 0


class TransactionCreate(TransactionBase):
    trade_id: int


class TransactionResponse(TransactionBase):
    id: int
    trade_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
