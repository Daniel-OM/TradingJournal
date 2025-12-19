"""
Router para watchlists
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.security import get_current_user
from app.models import Watchlist
from app.schemas import WatchlistCreate, WatchlistUpdate, WatchlistResponse

router = APIRouter(prefix="/watchlists", tags=["watchlists"])


@router.post("", response_model=WatchlistResponse)
async def create_watchlist(
    watchlist: WatchlistCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nueva watchlist"""
    db_watchlist = Watchlist(
        **watchlist.dict(),
        user_id=int(current_user["user_id"])
    )
    db.add(db_watchlist)
    db.commit()
    db.refresh(db_watchlist)
    return db_watchlist


@router.get("", response_model=List[WatchlistResponse])
async def list_watchlists(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Listar watchlists del usuario"""
    return db.query(Watchlist).filter(
        Watchlist.user_id == int(current_user["user_id"])
    ).offset(skip).limit(limit).all()


@router.get("/{watchlist_id}", response_model=WatchlistResponse)
async def get_watchlist(
    watchlist_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener una watchlist específica"""
    watchlist = db.query(Watchlist).filter(
        (Watchlist.id == watchlist_id) & (Watchlist.user_id == int(current_user["user_id"]))
    ).first()
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist no encontrada")
    return watchlist


@router.put("/{watchlist_id}", response_model=WatchlistResponse)
async def update_watchlist(
    watchlist_id: int,
    watchlist_update: WatchlistUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar una watchlist"""
    db_watchlist = db.query(Watchlist).filter(
        (Watchlist.id == watchlist_id) & (Watchlist.user_id == int(current_user["user_id"]))
    ).first()
    if not db_watchlist:
        raise HTTPException(status_code=404, detail="Watchlist no encontrada")
    
    update_data = watchlist_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_watchlist, key, value)
    
    db.commit()
    db.refresh(db_watchlist)
    return db_watchlist


@router.delete("/{watchlist_id}")
async def delete_watchlist(
    watchlist_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar una watchlist"""
    db_watchlist = db.query(Watchlist).filter(
        (Watchlist.id == watchlist_id) & (Watchlist.user_id == int(current_user["user_id"]))
    ).first()
    if not db_watchlist:
        raise HTTPException(status_code=404, detail="Watchlist no encontrada")
    
    db.delete(db_watchlist)
    db.commit()
    return {"message": "Watchlist eliminada"}
