"""
Modelo Media
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import BaseModel


class Media(BaseModel):
    """Archivos y imágenes asociados a trades"""
    __tablename__ = "media"
    
    trade_id = Column(Integer, ForeignKey('trades.id'), index=True)
    
    # Información del archivo
    url = Column(String(500))
    media_type = Column(String(50))  # image, document, chart, etc
    
    # Relaciones
    trade = relationship("Trade", back_populates="media")
