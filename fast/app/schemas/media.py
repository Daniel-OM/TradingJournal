"""
Schemas para Media
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MediaBase(BaseModel):
    url: str
    type: Optional[str] = None


class MediaCreate(MediaBase):
    trade_id: int


class MediaResponse(MediaBase):
    id: int
    trade_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
