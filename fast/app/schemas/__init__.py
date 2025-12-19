"""
Schemas de base de datos por entidad
"""

# User schemas
from .user import UserBase, UserCreate, UserUpdate, UserResponse

# Auth schemas
from .auth import TokenResponse, LoginRequest

# Strategy schemas
from .strategy import (
    StrategyBase,
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse,
)

# StrategyCondition schemas
from .strategy_condition import (
    StrategyConditionBase,
    StrategyConditionCreate,
    StrategyConditionUpdate,
    StrategyConditionResponse,
)

# Trade schemas
from .trade import TradeBase, TradeCreate, TradeUpdate, TradeResponse

# Watchlist schemas
from .watchlist import (
    WatchlistBase,
    WatchlistCreate,
    WatchlistUpdate,
    WatchlistResponse,
)

# WatchlistEntry schemas
from .watchlist_entry import (
    WatchlistEntryBase,
    WatchlistEntryCreate,
    WatchlistEntryUpdate,
    WatchlistEntryResponse,
)

# WatchlistCondition schemas
from .watchlist_condition import (
    WatchlistConditionBase,
    WatchlistConditionCreate,
    WatchlistConditionUpdate,
    WatchlistConditionResponse,
)

# Transaction schemas
from .transaction import TransactionBase, TransactionCreate, TransactionResponse

# Media schemas
from .media import MediaBase, MediaCreate, MediaResponse

# Error schemas
from .error import ErrorBase, ErrorCreate, ErrorUpdate, ErrorResponse

# Candle schemas
from .candle import CandleBase, CandleCreate, CandleResponse

# Setting schemas
from .setting import SettingBase, SettingCreate, SettingUpdate, SettingResponse

# Performance schemas
from .performance import PerformanceStats, SymbolPerformance, BestWorstSymbols, PerformanceData

# Asset schemas
from .asset import AssetBase, AssetCreate, AssetUpdate, AssetResponse

# Balance schemas
from .balance import AccountBalanceBase, AccountBalanceCreate, AccountBalanceUpdate, AccountBalanceResponse

# Level schemas
from .level import LevelBase, LevelCreate, LevelUpdate, LevelResponse

# Locate schemas
from .locate import LocateBase, LocateCreate, LocateUpdate, LocateResponse

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    # Auth
    "TokenResponse",
    "LoginRequest",
    # Strategy
    "StrategyBase",
    "StrategyCreate",
    "StrategyUpdate",
    "StrategyResponse",
    # StrategyCondition
    "StrategyConditionBase",
    "StrategyConditionCreate",
    "StrategyConditionUpdate",
    "StrategyConditionResponse",
    # Trade
    "TradeBase",
    "TradeCreate",
    "TradeUpdate",
    "TradeResponse",
    # Watchlist
    "WatchlistBase",
    "WatchlistCreate",
    "WatchlistUpdate",
    "WatchlistResponse",
    # WatchlistEntry
    "WatchlistEntryBase",
    "WatchlistEntryCreate",
    "WatchlistEntryUpdate",
    "WatchlistEntryResponse",
    # WatchlistCondition
    "WatchlistConditionBase",
    "WatchlistConditionCreate",
    "WatchlistConditionUpdate",
    "WatchlistConditionResponse",
    # Transaction
    "TransactionBase",
    "TransactionCreate",
    "TransactionResponse",
    # Media
    "MediaBase",
    "MediaCreate",
    "MediaResponse",
    # Error
    "ErrorBase",
    "ErrorCreate",
    "ErrorUpdate",
    "ErrorResponse",
    # Candle
    "CandleBase",
    "CandleCreate",
    "CandleResponse",
    # Setting
    "SettingBase",
    "SettingCreate",
    "SettingUpdate",
    "SettingResponse",
    # Performance
    "PerformanceStats",
    "SymbolPerformance",
    "BestWorstSymbols",
    "PerformanceData",
    # Asset
    "AssetBase",
    "AssetCreate",
    "AssetUpdate",
    "AssetResponse",
    # Balance
    "AccountBalanceBase",
    "AccountBalanceCreate",
    "AccountBalanceUpdate",
    "AccountBalanceResponse",
    # Level
    "LevelBase",
    "LevelCreate",
    "LevelUpdate",
    "LevelResponse",
    # Locate
    "LocateBase",
    "LocateCreate",
    "LocateUpdate",
    "LocateResponse",
]
