"""
Schemas para AccountBalance
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date


class AccountBalanceBase(BaseModel):
    date: date
    balance: float
    daily_return: Optional[float] = 0.0


class AccountBalanceCreate(AccountBalanceBase):
    user_id: int


class AccountBalanceUpdate(BaseModel):
    date: Optional[date] = None
    balance: Optional[float] = None
    daily_return: Optional[float] = None


class AccountBalanceResponse(AccountBalanceBase):
    id: int
    user_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
