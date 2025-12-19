"""
Modelos Watchlist
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base


class Watchlist(Base):
    """Listas de observación de activos"""
    __tablename__ = "watchlists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    
    # Información
    name = Column(String(255), index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relaciones
    user = relationship("User", back_populates="watchlists")
    entries = relationship("WatchlistEntry", back_populates="watchlist", cascade="all, delete-orphan")
    conditions = relationship("WatchlistCondition", back_populates="watchlist", cascade="all, delete-orphan")
