"""
Modelo para Locate (Ubicaciones de Shorts disponibles)
"""
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import BaseModel


class Locate(BaseModel):
    """Modelo de Locaciones de Shorts disponibles"""
    __tablename__ = "locates"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False, index=True, default=datetime.now(timezone.utc))
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    locate_type = Column(String(10), default='NORMAL')  # 'NORMAL' o 'REGSHOT'

    # Relationships
    user = relationship("User", back_populates="locates")
