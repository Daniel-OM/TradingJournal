"""
Modelo para WatchlistCondition (Condiciones de Watchlist)
"""
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, Table, Text
from sqlalchemy.orm import relationship

from app.db.database import Base

# Tabla de asociación para la relación muchos a muchos entre WatchlistEntry y WatchlistCondition
watchlist_entry_conditions = Table(
    'watchlist_entry_conditions',
    Base.metadata,
    Column('watchlist_entry_id', Integer, ForeignKey('watchlist_entries.id'), primary_key=True),
    Column('condition_id', Integer, ForeignKey('watchlist_conditions.id'), primary_key=True),
    Column('value', Float, default=0.0),
    Column('created_at', DateTime, default=datetime.now(timezone.utc))
)


class WatchlistCondition(Base):
    """Modelo de Condiciones de Watchlist para scoring"""
    __tablename__ = "watchlist_conditions"

    id = Column(Integer, primary_key=True, index=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationships
    watchlist = relationship("Watchlist", back_populates="conditions")
    entries = relationship(
        "WatchlistEntry",
        secondary=watchlist_entry_conditions,
        back_populates="conditions"
    )
