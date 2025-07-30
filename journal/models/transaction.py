
from datetime import date, datetime, timezone

from .base import Model, db

class Transaction(Model):
    __tablename__ = 'transaction'

    date = db.Column(db.Date, nullable=False, default=date.today)
    price = db.Column(db.Float, nullable=False)
    time = db.Column(db.String(10), default=datetime.now(timezone.utc).strftime('%H:%M:%S'))
    quantity = db.Column(db.Float, nullable=False)
    commission = db.Column(db.Float, nullable=False, default=1.0)
    type = db.Column(db.String(10), default='LONG')  # LONG/SHORT
    trade_id = db.Column(db.Integer, db.ForeignKey('trade.id'))
    
    trade = db.relationship('Trade', back_populates='transactions')

    def to_dict(self, exclude:list=[]):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'price': self.price,
            'time': self.time,
            'quantity': self.quantity,
            'commission': self.commission,
            'type': self.type,
            'trade_id': self.trade_id,
            'trade': {} if 'trade' in exclude else self.trade.to_dict(exclude=['transactions']+exclude),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }