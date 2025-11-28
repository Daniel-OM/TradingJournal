
from datetime import date, datetime, timezone
from flask_login import UserMixin

from .base import Model, db
from .setting import Risk

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
    risks = db.relationship('Risk', back_populates='user', lazy=True)
    
    def to_dict(self, exclude:list=[]):
        return {
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def getRiskAtDate(self, target_date:str|datetime|date):
        """
        Devuelve el Risk con la fecha más cercana (menor o igual) a target_date
        
        Args:
            target_date: puede ser date, datetime o string en formato 'YYYY-MM-DD'
            user_id: ID del usuario
            
        Returns:
            Risk object o None si no hay ninguno
        """
        
        # Convertir a date si es necesario
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        elif isinstance(target_date, datetime):
            target_date = target_date.date()

        if self.risks:
            # Filtrar risks con fecha <= target_date
            valid_risks = [r for r in self.risks if r.date <= target_date]
            
            # Si no hay risks válidos, retornar None
            if not valid_risks:
                return None
            
            # Retornar el risk con la fecha más cercana (máxima fecha)
            return max(valid_risks, key=lambda r: r.date)
        else:
            # Buscar el Risk con fecha <= target_date, ordenado descendente
            return Risk.query.filter(
                Risk.user_id == self.id,
                Risk.date <= target_date
            ).order_by(Risk.date.desc()).first()
            