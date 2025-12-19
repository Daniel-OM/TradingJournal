"""
Modelo para Asset (Activos/Valores)
"""
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Integer

from app.db.database import BaseModel


class Asset(BaseModel):
    """Modelo de Activos (Acciones, etc)"""
    __tablename__ = "assets"

    symbol = Column(String(20), nullable=False, unique=True, index=True)
    company_name = Column(String(200))
    description = Column(Text)
    exchange = Column(String(50))
    sector = Column(String(100))
    industry = Column(String(100))
    country = Column(String(100))
