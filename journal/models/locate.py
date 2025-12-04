
from datetime import datetime, timezone

from .base import Model, db
from .setting import Risk

class Locate(Model):
    __tablename__ = 'locate'

    date = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    symbol = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(10), nullable=False, default='NORMAL')  # 'NORMAL' o 'REGSHOT'
    
    user = db.relationship('User', back_populates='locates')

    def to_dict(self, exclude:list=[], force_dollars:bool=False):
        if self.user.settings[-1].show_r and not force_dollars:
            r: float = self.getRisk()
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'price': self.price,
            'quantity': self.quantity,
            'value': self.price * self.quantity / r if self.user.settings[-1].show_r and not force_dollars else self.price * self.quantity,
            'type': self.type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def getRisk(self) -> Risk:
        risk = self.user.getRiskAtDate(target_date=self.date)
        return 1.0 if risk is None else getattr(risk, 'risk', 1.0)