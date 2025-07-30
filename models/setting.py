
from datetime import date

from .base import Model, db

class Setting(Model):
    __tablename__ = 'setting'

    balance = db.Column(db.Float, nullable=False)
    commission = db.Column(db.Float, default=1.0)
    timezone = db.Column(db.String, default='UTC') # UTC, America/New_York, Europe/Madrid
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='settings')