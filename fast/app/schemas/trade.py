"""
Schemas para Trade
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .transaction import TransactionResponse
    from .media import MediaResponse
    from .strategy import StrategyResponse


class TradeBase(BaseModel):
    symbol: str
    company_name: Optional[str] = None
    entry_date: datetime
    entry_time: Optional[str] = None
    entry_price: float
    exit_date: Optional[datetime] = None
    exit_time: Optional[str] = None
    exit_price: Optional[float] = None
    quantity: float
    exit_quantity: Optional[float] = None
    trade_type: str  # LONG, SHORT
    balance: Optional[float] = None
    commission: float = 0
    profit_loss: Optional[float] = None
    description: Optional[str] = None
    why_profitable: Optional[str] = None
    influencing_factors: Optional[str] = None
    hashtags: Optional[str] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    strategy_id: Optional[int] = None


class TradeCreate(TradeBase):
    pass


class TradeUpdate(BaseModel):
    symbol: Optional[str] = None
    company_name: Optional[str] = None
    entry_date: Optional[datetime] = None
    entry_time: Optional[str] = None
    entry_price: Optional[float] = None
    exit_date: Optional[datetime] = None
    exit_time: Optional[str] = None
    exit_price: Optional[float] = None
    quantity: Optional[float] = None
    exit_quantity: Optional[float] = None
    trade_type: Optional[str] = None
    balance: Optional[float] = None
    commission: Optional[float] = None
    profit_loss: Optional[float] = None
    description: Optional[str] = None
    why_profitable: Optional[str] = None
    influencing_factors: Optional[str] = None
    hashtags: Optional[str] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    strategy_id: Optional[int] = None


class TradeResponse(TradeBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

