"""
Schemas para WatchlistCondition
"""

from pydantic import BaseModel
from typing import Optional


class WatchlistConditionBase(BaseModel):
    name: str
    description: Optional[str] = None
    score: Optional[float] = 1.0


class WatchlistConditionCreate(WatchlistConditionBase):
    watchlist_id: int


class WatchlistConditionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    score: Optional[float] = None


class WatchlistConditionResponse(WatchlistConditionBase):
    id: int
    watchlist_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
