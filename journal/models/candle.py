
from datetime import datetime, timezone
from .base import Model, db

class Candle(Model):
    __tablename__ = 'candle'

    symbol = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    open = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float, nullable=True)
    session = db.Column(db.String, nullable=True, default='REG') # PRE, REG, POST
    timeframe = db.Column(db.String, nullable=False)
    
    def to_dict(self, exclude:list=[]):
        return {
            'id': self.id,
            'date': self.date.replace(tzinfo=timezone.utc).strftime('%Y-%m-%d %H:%M:%S%z'),
            'symbol': self.symbol,
            'open': float(self.open),
            'high': float(self.high),
            'low': float(self.low),
            'close': float(self.close),
            'volume': float(self.volume),
            'session': self.session,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }