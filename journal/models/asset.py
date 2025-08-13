
from datetime import date, datetime, timezone
from sqlalchemy import and_

from .base import Model, db

class Asset(Model):
    __tablename__ = 'assets'

    symbol = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(200))
    description = db.Column(db.Text)
    exchange = db.Column(db.String(50))
    sector = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    country = db.Column(db.String(100))
    
    def to_dict(self, exclude:list=[]):
        return {
            'symbol': self.symbol,
            'company_name': self.company_name,
            'description': self.description,
            'exchange': self.exchange,
            'sector': self.sector,
            'industry': self.industry,
            'country': self.country,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }