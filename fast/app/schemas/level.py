"""
Schemas para Level
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date


class LevelBase(BaseModel):
    date: date
    symbol: str
    price: float
    level_type: Optional[str] = "support"


class LevelCreate(LevelBase):
    pass


class LevelUpdate(BaseModel):
    date: Optional[date] = None
    symbol: Optional[str] = None
    price: Optional[float] = None
    level_type: Optional[str] = None


class LevelResponse(LevelBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
