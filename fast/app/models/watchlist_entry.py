"""
Watchlist Entry model - individual entries in a watchlist
"""

from datetime import date, datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.db.database import Base

# Association table for watchlist entries and levels
watchlist_entry_levels = Table(
    'watchlist_entry_levels',
    Base.metadata,
    Column('watchlist_entry_id', Integer, ForeignKey('watchlist_entries.id'), primary_key=True),
    Column('level_id', Integer, ForeignKey('levels.id'), primary_key=True)
)

# Association table for watchlist entries and conditions
watchlist_entry_conditions = Table(
    'watchlist_entry_conditions',
    Base.metadata,
    Column('watchlist_entry_id', Integer, ForeignKey('watchlist_entries.id'), primary_key=True),
    Column('condition_id', Integer, ForeignKey('watchlist_conditions.id'), primary_key=True),
    Column('value', Float, default=0.0),
    Column('created_at', DateTime, default=datetime.now(timezone.utc))
)


class WatchlistEntry(Base):
    """
    Watchlist entry model - individual stocks/assets in a watchlist
    """
    __tablename__ = 'watchlist_entries'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, default=date.today)
    symbol = Column(String(20), nullable=False)
    company_name = Column(String(200), nullable=True)
    
    # Price and volume data
    price = Column(Float, nullable=True)
    atr = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    avg_volume = Column(Float, nullable=True)
    
    # Fundamental data
    market_cap = Column(Float, nullable=True)
    float_shares = Column(Float, nullable=True)
    per = Column(Float, nullable=True)  # Price-to-Earnings
    eps = Column(Float, nullable=True)  # Earnings per Share
    current_ratio = Column(Float, nullable=True)
    
    # Classification
    exchange = Column(String(50), nullable=True)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Analysis
    score = Column(Float, nullable=False, default=0.0)
    description = Column(Text, nullable=True)
    negative_action = Column(Text, nullable=True)
    hashtags = Column(String(500), nullable=True)
    risk_reward = Column(String(20), nullable=True)
    profit_target = Column(Float, nullable=True)
    other_notes = Column(Text, nullable=True)
    
    # Exit
    date_exit = Column(Date, nullable=True)
    
    # Foreign key
    watchlist_id = Column(Integer, ForeignKey('watchlists.id'), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    watchlist = relationship('Watchlist', back_populates='entries')
    levels = relationship(
        'Level',
        secondary=watchlist_entry_levels,
        back_populates='watchlist_entries'
    )
    conditions = relationship(
        'WatchlistCondition',
        secondary=watchlist_entry_conditions,
        back_populates='watchlist_entries'
    )
