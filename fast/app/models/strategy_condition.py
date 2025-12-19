"""
Strategy Condition model
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.db.database import Base

# Association table for trades and strategy conditions
trade_scoring = Table(
    'trade_scoring',
    Base.metadata,
    Column('trade_id', Integer, ForeignKey('trades.id'), primary_key=True),
    Column('strategy_condition_id', Integer, ForeignKey('strategy_conditions.id'), primary_key=True)
)


class StrategyCondition(Base):
    """
    Strategy condition model - conditions/rules for a strategy
    """
    __tablename__ = 'strategy_conditions'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    score = Column(Integer, default=10)
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=False)

    # Relationships
    strategy = relationship('Strategy', back_populates='conditions')
    trades = relationship(
        'Trade',
        secondary=trade_scoring,
        back_populates='conditions'
    )
