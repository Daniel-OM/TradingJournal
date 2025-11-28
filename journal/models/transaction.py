
from datetime import date, datetime, timezone

from .base import Model, db
from .setting import Risk

class Transaction(Model):
    __tablename__ = 'transaction'

    date = db.Column(db.Date, nullable=False, default=date.today)
    price = db.Column(db.Float, nullable=False)
    time = db.Column(db.String(10), default=datetime.now(timezone.utc).strftime('%H:%M:%S'))
    quantity = db.Column(db.Float, nullable=False)
    commission = db.Column(db.Float, nullable=False, default=0.0)
    ecn_fee = db.Column(db.Float, nullable=True, default=0.0)
    locates = db.Column(db.Float, nullable=True, default=0.0)
    type = db.Column(db.String(10), default='LONG')  # LONG/SHORT
    trade_id = db.Column(db.Integer, db.ForeignKey('trade.id'))
    
    trade = db.relationship('Trade', back_populates='transactions')

    def to_dict(self, exclude:list=[], force_dollars:bool=False):
        if self.trade.user.settings[-1].show_r and not force_dollars:
            r: float = self.getRisk()
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'price': self.price,
            'time': self.time,
            'quantity': self.quantity,
            'commission': self.commission / r if self.trade.user.settings[-1].show_r and self.commission and not force_dollars else self.commission,
            'ecn_fee': self.ecn_fee / r if self.trade.user.settings[-1].show_r and self.ecn_fee and not force_dollars else self.ecn_fee,
            'locates': self.locates / r if self.trade.user.settings[-1].show_r and self.locates and not force_dollars else self.locates,
            'type': self.type,
            'trade_id': self.trade_id,
            'trade': {} if 'trade' in exclude else self.trade.to_dict(exclude=['transactions']+exclude, force_dollars=force_dollars),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @property
    def datetime(self) -> datetime:
        
        time_str = self.time or '00:00:00'
        
        if len(time_str.split(':')) == 2:
            time_str += ':00'
        
        return datetime.combine(self.date, datetime.strptime(time_str, '%H:%M:%S').time(), tzinfo=timezone.utc)
        
    def getRisk(self) -> Risk:
        risk = self.trade.user.getRiskAtDate(target_date=self.date)
        return 1.0 if risk is None else getattr(risk, 'risk', 1.0)