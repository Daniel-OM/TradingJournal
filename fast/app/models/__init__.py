"""
Modelos de base de datos por entidad
"""

from .user import User
from .trade import Trade, trade_scoring as trade_scoring_trade
from .strategy import Strategy, StrategyCondition
from .watchlist import Watchlist
from .watchlist_entry import WatchlistEntry, watchlist_entry_levels, watchlist_entry_conditions
from .watchlist_condition import WatchlistCondition
from .transaction import Transaction
from .media import Media
from .error import Error
from .candle import Candle
from .setting import Setting
from .asset import Asset
from .balance import AccountBalance
from .level import Level, watchlist_entry_levels as level_association
from .locate import Locate
from .base import Base, BaseModel

# Tablas de asociación
from .level import watchlist_entry_levels

__all__ = [
    "User",
    "Trade",
    "Strategy",
    "StrategyCondition",
    "Watchlist",
    "WatchlistEntry",
    "WatchlistCondition",
    "Transaction",
    "Media",
    "Error",
    "Candle",
    "Setting",
    "Asset",
    "AccountBalance",
    "Level",
    "Locate",
    "Base",
    "BaseModel",
    "watchlist_entry_levels",
    "watchlist_entry_conditions",
    "trade_scoring_trade",
]
