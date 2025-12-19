"""
Modelo para Level (Niveles de Soporte/Resistencia)
"""
from datetime import date, datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Date, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.db.database import BaseModel

# Tabla de asociación para la relación muchos a muchos entre WatchlistEntry y Level
watchlist_entry_levels = Table(
    'watchlist_entry_levels',
    BaseModel.metadata,
    Column('watchlist_entry_id', Integer, ForeignKey('watchlist_entries.id'), primary_key=True),
    Column('level_id', Integer, ForeignKey('levels.id'), primary_key=True),
    Column('impact_level', String(10), default='medium'),  # low, medium, high
    Column('created_at', DateTime, default=datetime.now(timezone.utc))
)


class Level(BaseModel):
    """Modelo de Niveles de Soporte/Resistencia"""
    __tablename__ = "levels"

    date = Column(Date, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)

    # Relationships
    watchlist_entries = relationship(
        "WatchlistEntry",
        secondary=watchlist_entry_levels,
        back_populates="levels"
    )
