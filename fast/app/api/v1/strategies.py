"""
Router para estrategias
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.security import get_current_user
from app.models import Strategy
from app.schemas import StrategyCreate, StrategyUpdate, StrategyResponse

router = APIRouter(prefix="/strategies", tags=["strategies"])


@router.post("", response_model=StrategyResponse)
async def create_strategy(
    strategy: StrategyCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nueva estrategia"""
    db_strategy = Strategy(
        **strategy.dict(),
        user_id=int(current_user["user_id"])
    )
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy


@router.get("", response_model=List[StrategyResponse])
async def list_strategies(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Listar estrategias del usuario"""
    return db.query(Strategy).filter(
        Strategy.user_id == int(current_user["user_id"])
    ).offset(skip).limit(limit).all()


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener una estrategia específica"""
    strategy = db.query(Strategy).filter(
        (Strategy.id == strategy_id) & (Strategy.user_id == int(current_user["user_id"]))
    ).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Estrategia no encontrada")
    return strategy


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: int,
    strategy_update: StrategyUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar una estrategia"""
    db_strategy = db.query(Strategy).filter(
        (Strategy.id == strategy_id) & (Strategy.user_id == int(current_user["user_id"]))
    ).first()
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Estrategia no encontrada")
    
    update_data = strategy_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_strategy, key, value)
    
    db.commit()
    db.refresh(db_strategy)
    return db_strategy


@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar una estrategia"""
    db_strategy = db.query(Strategy).filter(
        (Strategy.id == strategy_id) & (Strategy.user_id == int(current_user["user_id"]))
    ).first()
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Estrategia no encontrada")
    
    db.delete(db_strategy)
    db.commit()
    return {"message": "Estrategia eliminada"}
