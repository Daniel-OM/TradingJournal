
from datetime import date, datetime, timezone
from sqlalchemy import and_

from .base import Model, db

class WatchlistCondition(Model):
    __tablename__ = 'watchlist_condition'

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    score = db.Column(db.Float, default=1.0)
    watchlist_id = db.Column(db.Integer, db.ForeignKey('watchlist.id'))
    
    watchlist = db.relationship('Watchlist', back_populates='conditions')
    entries = db.relationship('WatchlistEntry', secondary='watchlist_scoring', back_populates='conditions')
    
    def to_dict(self, exclude:list=[]):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'score': self.score,
            'watchlist': {} if 'watchlist' in exclude else self.watchlist.to_dict(exclude=['conditions', 'entries']+exclude),
            'entries': {} if 'entries' in exclude else [e.to_dict(exclude=['conditions', 'watchlist']+exclude) for e in self.entries], 
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }