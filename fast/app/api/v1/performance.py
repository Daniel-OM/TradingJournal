"""
Router para performance
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.database import get_db
from app.core.security import get_current_user
from app.models import Trade
from app.services.performance import PerformanceCalculator, SymbolPerformanceCalculator

router = APIRouter(prefix="/performance", tags=["performance"])


@router.get("/stats")
async def get_performance_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    symbol: Optional[str] = None,
    strategy_id: Optional[int] = None,
    gross: bool = False,
):
    """Obtener estadísticas de performance"""
    query = db.query(Trade).filter(Trade.user_id == int(current_user["user_id"]))
    
    if symbol:
        query = query.filter(Trade.symbol == symbol.upper())
    if strategy_id:
        query = query.filter(Trade.strategy_id == strategy_id)
    if start_date:
        query = query.filter(Trade.entry_date >= start_date)
    if end_date:
        query = query.filter(Trade.entry_date <= end_date)
    
    trades = query.all()
    
    # Convertir trades a diccionarios
    trades_data = []
    for trade in trades:
        trades_data.append({
            'symbol': trade.symbol,
            'entry_date': trade.entry_date,
            'exit_date': trade.exit_date,
            'profit_loss': trade.profit_loss or 0,
            'commission': trade.commission or 0,
            'exit_quantity': trade.exit_quantity or trade.quantity,
        })
    
    # Calcular estadísticas
    calculator = PerformanceCalculator(trades_data, gross=gross)
    stats = calculator.get_stats()
    
    return {"stats": stats}


@router.get("/symbols")
async def get_symbols_performance(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    gross: bool = False,
    top_n: int = Query(5, ge=1, le=20),
):
    """Obtener performance por símbolo (mejores y peores)"""
    query = db.query(Trade).filter(Trade.user_id == int(current_user["user_id"]))
    
    if start_date:
        query = query.filter(Trade.entry_date >= start_date)
    if end_date:
        query = query.filter(Trade.entry_date <= end_date)
    
    trades = query.all()
    
    # Convertir trades a diccionarios
    trades_data = []
    for trade in trades:
        trades_data.append({
            'symbol': trade.symbol,
            'profit_loss': trade.profit_loss or 0,
            'commission': trade.commission or 0,
            'exit_quantity': trade.exit_quantity or trade.quantity,
        })
    
    # Calcular estadísticas por símbolo
    calculator = SymbolPerformanceCalculator(trades_data, gross=gross)
    best_worst = calculator.get_best_and_worst_symbols(top_n=top_n)
    
    return best_worst
