"""
Router para trades
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.core.security import get_current_user
from app.models import Trade
from app.schemas import TradeCreate, TradeUpdate, TradeResponse

router = APIRouter(prefix="/trades", tags=["trades"])


@router.post("", response_model=TradeResponse)
async def create_trade(
    trade: TradeCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nuevo trade"""
    db_trade = Trade(
        **trade.dict(),
        user_id=int(current_user["user_id"])
    )
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade


@router.get("", response_model=List[TradeResponse])
async def list_trades(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    symbol: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    trade_type: Optional[str] = None,
):
    """Listar trades del usuario"""
    query = db.query(Trade).filter(Trade.user_id == int(current_user["user_id"]))
    
    if symbol:
        query = query.filter(Trade.symbol == symbol.upper())
    if trade_type:
        query = query.filter(Trade.trade_type == trade_type.upper())
    if start_date:
        query = query.filter(Trade.entry_date >= start_date)
    if end_date:
        query = query.filter(Trade.entry_date <= end_date)
    
    return query.offset(skip).limit(limit).all()


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener un trade específico"""
    trade = db.query(Trade).filter(
        (Trade.id == trade_id) & (Trade.user_id == int(current_user["user_id"]))
    ).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade no encontrado")
    return trade


@router.put("/{trade_id}", response_model=TradeResponse)
async def update_trade(
    trade_id: int,
    trade_update: TradeUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar un trade"""
    db_trade = db.query(Trade).filter(
        (Trade.id == trade_id) & (Trade.user_id == int(current_user["user_id"]))
    ).first()
    if not db_trade:
        raise HTTPException(status_code=404, detail="Trade no encontrado")
    
    update_data = trade_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_trade, key, value)
    
    db.commit()
    db.refresh(db_trade)
    return db_trade


@router.delete("/{trade_id}")
async def delete_trade(
    trade_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar un trade"""
    db_trade = db.query(Trade).filter(
        (Trade.id == trade_id) & (Trade.user_id == int(current_user["user_id"]))
    ).first()
    if not db_trade:
        raise HTTPException(status_code=404, detail="Trade no encontrado")
    
    db.delete(db_trade)
    db.commit()
    return {"message": "Trade eliminado"}
