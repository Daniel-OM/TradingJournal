"""
Schemas para Performance
"""

from pydantic import BaseModel
from typing import List


class PerformanceStats(BaseModel):
    total_pnl: float
    winning_trades: int
    losing_trades: int
    scratch_trades: int
    win_rate: float
    loss_rate: float
    winning_pnl: float
    losing_pnl: float
    avg_trade_pnl: float
    avg_pnl_per_share: float
    median_trade_pnl: float
    avg_win: float
    avg_loss: float
    largest_gain: float
    largest_loss: float
    risk_reward: float
    total_wins: float
    total_losses: float
    profit_factor: float
    trade_pnl_std: float
    sharpe_ratio: float
    max_drawdown: float
    sqn: float
    k_ratio: float
    kelly_percent: float
    p_value: float
    max_consecutive_wins: int
    max_consecutive_losses: int
    avg_daily_pnl: float
    avg_daily_volume: float
    avg_win_per_day: float
    avg_loss_per_day: float
    daily_winrate: float
    avg_trades_per_day: float


class SymbolPerformance(BaseModel):
    symbol: str
    total_pnl: float
    avg_pnl: float
    win_rate: float
    trade_count: int
    avg_win: float
    avg_loss: float


class BestWorstSymbols(BaseModel):
    best: List[SymbolPerformance]
    worst: List[SymbolPerformance]


class PerformanceData(BaseModel):
    stats: PerformanceStats
    best_worst_symbols: BestWorstSymbols
