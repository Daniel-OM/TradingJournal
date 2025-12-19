"""
Rutas para gestionar Activos (Assets)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Asset
from app.schemas import AssetBase, AssetCreate, AssetUpdate, AssetResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[AssetResponse])
async def list_assets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todos los activos"""
    assets = db.query(Asset).offset(skip).limit(limit).all()
    return assets


@router.get("/{symbol}", response_model=AssetResponse)
async def get_asset(symbol: str, db: Session = Depends(get_db)):
    """Obtener un activo por símbolo"""
    asset = db.query(Asset).filter(Asset.symbol == symbol.upper()).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return asset


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset: AssetCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Crear un nuevo activo"""
    # Verificar que el usuario sea admin (opcional)
    existing_asset = db.query(Asset).filter(Asset.symbol == asset.symbol.upper()).first()
    if existing_asset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Asset with this symbol already exists"
        )
    
    db_asset = Asset(**asset.model_dump())
    db_asset.symbol = db_asset.symbol.upper()
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


@router.put("/{symbol}", response_model=AssetResponse)
async def update_asset(
    symbol: str,
    asset_update: AssetUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Actualizar un activo"""
    asset = db.query(Asset).filter(Asset.symbol == symbol.upper()).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    
    update_data = asset_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(asset, key, value)
    
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    symbol: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Eliminar un activo"""
    asset = db.query(Asset).filter(Asset.symbol == symbol.upper()).first()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    
    db.delete(asset)
    db.commit()
    return None
