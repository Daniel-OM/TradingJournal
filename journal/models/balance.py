
from datetime import date

from .base import Model, db

class AccountBalance(Model):
    __tablename__ = 'balance'

    date = db.Column(db.Date, nullable=False, unique=True, default=date.today())
    balance = db.Column(db.Float, nullable=False)
    daily_return = db.Column(db.Float, default=0)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='balances')