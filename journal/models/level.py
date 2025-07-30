
from datetime import date, datetime, timezone

from .base import Model, db

# Tabla de asociación para la relación muchos a muchos entre Watchlist y Level
watchlist_levels = db.Table('watchlist_levels',
    db.Column('watchlist_entry_id', db.Integer, db.ForeignKey('watchlist_entry.id'), primary_key=True),
    db.Column('level_id', db.Integer, db.ForeignKey('level.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.now(timezone.utc)),
    db.Column('impact_level', db.String(10), default='medium')  # low, medium, high
)

class Level(Model):
    __tablename__ = 'level'

    date = db.Column(db.Date, nullable=False, default=date.today)
    symbol = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    entries = db.relationship('WatchlistEntry', secondary=watchlist_levels, back_populates='levels')
    
    def to_dict(self, exclude:list=[]):
        return {
            'id': self.id,
            'date': self.date,
            'symbol': self.symbol,
            'price': self.price,
            'entries': [] if 'entries' in exclude else [e.to_dict(exclude=['levels']) for e in self.entries],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }