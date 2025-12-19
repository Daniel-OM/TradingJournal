"""
Rutas para gestionar Saldo de Cuenta
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from app.db.database import get_db
from app.models import AccountBalance
from app.schemas import AccountBalanceResponse, AccountBalanceCreate, AccountBalanceUpdate
from app.core.security import get_current_user

router = APIRouter(prefix="/balance", tags=["balance"])


@router.get("", response_model=list[AccountBalanceResponse])
async def list_balance(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Listar saldos del usuario"""
    balances = db.query(AccountBalance).filter(
        AccountBalance.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return balances


@router.get("/{date_str}", response_model=AccountBalanceResponse)
async def get_balance(
    date_str: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener saldo de una fecha específica"""
    try:
        balance_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    balance = db.query(AccountBalance).filter(
        AccountBalance.user_id == current_user.id,
        AccountBalance.date == balance_date
    ).first()
    
    if not balance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Balance not found")
    return balance


@router.post("", response_model=AccountBalanceResponse, status_code=status.HTTP_201_CREATED)
async def create_balance(
    balance_data: AccountBalanceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Crear un nuevo registro de saldo"""
    # Verificar que no exista un saldo para esa fecha
    existing = db.query(AccountBalance).filter(
        AccountBalance.user_id == current_user.id,
        AccountBalance.date == balance_data.date
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Balance for this date already exists"
        )
    
    db_balance = AccountBalance(
        **balance_data.model_dump(),
        user_id=current_user.id
    )
    db.add(db_balance)
    db.commit()
    db.refresh(db_balance)
    return db_balance


@router.put("/{date_str}", response_model=AccountBalanceResponse)
async def update_balance(
    date_str: str,
    balance_update: AccountBalanceUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Actualizar un registro de saldo"""
    try:
        balance_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    balance = db.query(AccountBalance).filter(
        AccountBalance.user_id == current_user.id,
        AccountBalance.date == balance_date
    ).first()
    
    if not balance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Balance not found")
    
    update_data = balance_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(balance, key, value)
    
    db.add(balance)
    db.commit()
    db.refresh(balance)
    return balance


@router.delete("/{date_str}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_balance(
    date_str: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Eliminar un registro de saldo"""
    try:
        balance_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    balance = db.query(AccountBalance).filter(
        AccountBalance.user_id == current_user.id,
        AccountBalance.date == balance_date
    ).first()
    
    if not balance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Balance not found")
    
    db.delete(balance)
    db.commit()
    return None
