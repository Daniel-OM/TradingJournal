
from .base import Model, db

class Media(Model):
    __tablename__ = 'media'

    url = db.Column(db.String(500), nullable=False)
    trade_id = db.Column(db.Integer, db.ForeignKey('trade.id'))
    
    trade = db.relationship('Trade', back_populates='media')
    
    def to_dict(self, exclude:list=[]):
        return {
            'id': self.id,
            'url': self.url.replace('\\', '/'),
            'trade_id': self.trade_id,
            'trade': {} if 'trade' in exclude else self.trade.to_dict(exclude=['media']+exclude),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }