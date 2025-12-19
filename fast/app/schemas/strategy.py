"""
Schemas para Strategy
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class StrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class StrategyCreate(StrategyBase):
    pass


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class StrategyResponse(StrategyBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
