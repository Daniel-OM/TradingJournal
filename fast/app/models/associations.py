"""
Tablas de asociación (many-to-many)
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Table, Float
from datetime import datetime, timezone
from app.db.database import BaseModel


# Tabla de asociación para Trade-StrategyCondition
trade_scoring = Table(
    'trade_scoring',
    BaseModel.metadata,
    Column('trade_id', Integer, ForeignKey('trades.id'), primary_key=True),
    Column('scoring_id', Integer, ForeignKey('strategy_conditions.id'), primary_key=True),
    Column('value', Float, nullable=True, default=0.0),
    Column('created_at', DateTime, default=datetime.now(timezone.utc)),
)

