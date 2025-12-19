"""
Schemas de StrategyCondition
"""

from pydantic import BaseModel
from typing import Optional


class StrategyConditionBase(BaseModel):
    """Base schema for StrategyCondition"""
    name: str
    description: Optional[str] = None
    score: float = 10


class StrategyConditionCreate(StrategyConditionBase):
    """Schema for creating StrategyCondition"""
    strategy_id: int


class StrategyConditionUpdate(BaseModel):
    """Schema for updating StrategyCondition"""
    name: Optional[str] = None
    description: Optional[str] = None
    score: Optional[float] = None


class StrategyConditionResponse(StrategyConditionBase):
    """Schema for responding with StrategyCondition"""
    id: int
    strategy_id: int
    created_at: str

    class Config:
        from_attributes = True
