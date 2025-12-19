"""
Rutas para gestionar Locaciones de Shorts
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Locate
from app.schemas import LocateResponse, LocateCreate, LocateUpdate
from app.core.security import get_current_user

router = APIRouter(prefix="/locates", tags=["locates"])


@router.get("", response_model=list[LocateResponse])
async def list_locates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Listar locaciones del usuario"""
    locates = db.query(Locate).filter(
        Locate.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return locates


@router.get("/{locate_id}", response_model=LocateResponse)
async def get_locate(
    locate_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener una locación específica"""
    locate = db.query(Locate).filter(
        Locate.id == locate_id,
        Locate.user_id == current_user.id
    ).first()
    
    if not locate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Locate not found")
    return locate


@router.post("", response_model=LocateResponse, status_code=status.HTTP_201_CREATED)
async def create_locate(
    locate: LocateCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Crear una nueva locación"""
    db_locate = Locate(
        **locate.model_dump(),
        user_id=current_user.id
    )
    db.add(db_locate)
    db.commit()
    db.refresh(db_locate)
    return db_locate


@router.put("/{locate_id}", response_model=LocateResponse)
async def update_locate(
    locate_id: int,
    locate_update: LocateUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Actualizar una locación"""
    locate = db.query(Locate).filter(
        Locate.id == locate_id,
        Locate.user_id == current_user.id
    ).first()
    
    if not locate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Locate not found")
    
    update_data = locate_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(locate, key, value)
    
    db.add(locate)
    db.commit()
    db.refresh(locate)
    return locate


@router.delete("/{locate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_locate(
    locate_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Eliminar una locación"""
    locate = db.query(Locate).filter(
        Locate.id == locate_id,
        Locate.user_id == current_user.id
    ).first()
    
    if not locate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Locate not found")
    
    db.delete(locate)
    db.commit()
    return None
