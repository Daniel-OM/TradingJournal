"""
Routers de la API v1
"""

from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .trades import router as trades_router
from .strategies import router as strategies_router
from .watchlists import router as watchlists_router
from .watchlist_entry import router as watchlist_entry_router
from .performance import router as performance_router
from .asset import router as asset_router
from .balance import router as balance_router
from .level import router as level_router
from .locate import router as locate_router
from .strategy_condition import router as strategy_condition_router

# Crear router principal
router = APIRouter()

# Incluir todos los routers
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(trades_router)
router.include_router(strategies_router)
router.include_router(watchlists_router)
router.include_router(watchlist_entry_router)
router.include_router(performance_router)
router.include_router(asset_router)
router.include_router(balance_router)
router.include_router(level_router)
router.include_router(locate_router)
router.include_router(strategy_condition_router)

__all__ = ["router"]