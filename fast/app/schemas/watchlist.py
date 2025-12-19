"""
Schemas para Watchlist
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class WatchlistBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class WatchlistCreate(WatchlistBase):
    pass


class WatchlistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class WatchlistResponse(WatchlistBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
