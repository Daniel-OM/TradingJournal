
from datetime import date, datetime, timezone
from flask_login import UserMixin

from .base import Model, db

class User(Model, UserMixin):
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    
    balances = db.relationship('AccountBalance', back_populates='user', lazy=True)
    errors = db.relationship('Error', back_populates='user', lazy=True)
    settings = db.relationship('Setting', back_populates='user', lazy=True)
    strategies = db.relationship('Strategy', back_populates='user', lazy=True)
    trades = db.relationship('Trade', back_populates='user', lazy=True)
    watchlists = db.relationship('Watchlist', back_populates='user', lazy=True)