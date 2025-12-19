"""
Strategy Condition endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import StrategyCondition
from app.schemas import StrategyConditionBase, StrategyConditionCreate, StrategyConditionUpdate, StrategyConditionResponse
from app.routers.dependencies import get_current_user

router = APIRouter(prefix="/strategy-conditions", tags=["strategy-conditions"])


@router.get("", response_model=list[StrategyConditionResponse])
async def list_strategy_conditions(
    strategy_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """List all strategy conditions for a specific strategy"""
    conditions = db.query(StrategyCondition).filter(
        StrategyCondition.strategy_id == strategy_id
    ).all()
    return conditions


@router.get("/{condition_id}", response_model=StrategyConditionResponse)
async def get_strategy_condition(
    condition_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get a specific strategy condition"""
    condition = db.query(StrategyCondition).filter(
        StrategyCondition.id == condition_id
    ).first()
    
    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy condition not found"
        )
    
    return condition


@router.post("", response_model=StrategyConditionResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy_condition(
    condition: StrategyConditionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Create a new strategy condition"""
    db_condition = StrategyCondition(
        name=condition.name,
        description=condition.description,
        score=condition.score,
        strategy_id=condition.strategy_id,
    )
    db.add(db_condition)
    db.commit()
    db.refresh(db_condition)
    return db_condition


@router.put("/{condition_id}", response_model=StrategyConditionResponse)
async def update_strategy_condition(
    condition_id: int,
    condition_update: StrategyConditionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Update a strategy condition"""
    condition = db.query(StrategyCondition).filter(
        StrategyCondition.id == condition_id
    ).first()
    
    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy condition not found"
        )
    
    if condition_update.name is not None:
        condition.name = condition_update.name
    if condition_update.description is not None:
        condition.description = condition_update.description
    if condition_update.score is not None:
        condition.score = condition_update.score
    
    db.commit()
    db.refresh(condition)
    return condition


@router.delete("/{condition_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy_condition(
    condition_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Delete a strategy condition"""
    condition = db.query(StrategyCondition).filter(
        StrategyCondition.id == condition_id
    ).first()
    
    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy condition not found"
        )
    
    db.delete(condition)
    db.commit()
