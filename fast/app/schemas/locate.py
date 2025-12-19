"""
Schemas para Locate
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LocateBase(BaseModel):
    date: datetime
    symbol: str
    price: float
    quantity: int
    locate_type: Optional[str] = "NORMAL"


class LocateCreate(LocateBase):
    pass


class LocateUpdate(BaseModel):
    date: Optional[datetime] = None
    symbol: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    locate_type: Optional[str] = None


class LocateResponse(LocateBase):
    id: int
    user_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
