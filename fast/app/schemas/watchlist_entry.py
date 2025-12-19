"""
Schemas de WatchlistEntry
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class WatchlistEntryBase(BaseModel):
    """Base schema for WatchlistEntry"""
    date: date
    symbol: str
    company_name: Optional[str] = None
    price: Optional[float] = None
    atr: Optional[float] = None
    volume: Optional[float] = None
    avg_volume: Optional[float] = None
    market_cap: Optional[float] = None
    float_shares: Optional[float] = None
    per: Optional[float] = None  # Price-to-Earnings
    eps: Optional[float] = None
    current_ratio: Optional[float] = None
    exchange: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    score: float = 0.0
    description: Optional[str] = None
    negative_action: Optional[str] = None
    hashtags: Optional[str] = None
    risk_reward: Optional[str] = None
    profit_target: Optional[float] = None
    other_notes: Optional[str] = None
    date_exit: Optional[date] = None


class WatchlistEntryCreate(WatchlistEntryBase):
    """Schema for creating WatchlistEntry"""
    watchlist_id: int


class WatchlistEntryUpdate(BaseModel):
    """Schema for updating WatchlistEntry"""
    date: Optional[date] = None
    symbol: Optional[str] = None
    company_name: Optional[str] = None
    price: Optional[float] = None
    atr: Optional[float] = None
    volume: Optional[float] = None
    avg_volume: Optional[float] = None
    market_cap: Optional[float] = None
    float_shares: Optional[float] = None
    per: Optional[float] = None
    eps: Optional[float] = None
    current_ratio: Optional[float] = None
    exchange: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    score: Optional[float] = None
    description: Optional[str] = None
    negative_action: Optional[str] = None
    hashtags: Optional[str] = None
    risk_reward: Optional[str] = None
    profit_target: Optional[float] = None
    other_notes: Optional[str] = None
    date_exit: Optional[date] = None


class WatchlistEntryResponse(WatchlistEntryBase):
    """Schema for responding with WatchlistEntry"""
    id: int
    watchlist_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
