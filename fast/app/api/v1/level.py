"""
Rutas para gestionar Niveles de Soporte/Resistencia
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Level
from app.schemas import LevelResponse, LevelCreate, LevelUpdate
from app.core.security import get_current_user

router = APIRouter(prefix="/levels", tags=["levels"])


@router.get("", response_model=list[LevelResponse])
async def list_levels(
    skip: int = 0,
    limit: int = 100,
    symbol: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Listar niveles, opcionalmente filtrados por símbolo"""
    query = db.query(Level)
    
    if symbol:
        query = query.filter(Level.symbol == symbol.upper())
    
    levels = query.offset(skip).limit(limit).all()
    return levels


@router.get("/{level_id}", response_model=LevelResponse)
async def get_level(
    level_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtener un nivel específico"""
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Level not found")
    return level


@router.post("", response_model=LevelResponse, status_code=status.HTTP_201_CREATED)
async def create_level(
    level: LevelCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Crear un nuevo nivel"""
    db_level = Level(**level.model_dump())
    db.add(db_level)
    db.commit()
    db.refresh(db_level)
    return db_level


@router.put("/{level_id}", response_model=LevelResponse)
async def update_level(
    level_id: int,
    level_update: LevelUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Actualizar un nivel"""
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Level not found")
    
    update_data = level_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(level, key, value)
    
    db.add(level)
    db.commit()
    db.refresh(level)
    return level


@router.delete("/{level_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_level(
    level_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Eliminar un nivel"""
    level = db.query(Level).filter(Level.id == level_id).first()
    if not level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Level not found")
    
    db.delete(level)
    db.commit()
    return None
