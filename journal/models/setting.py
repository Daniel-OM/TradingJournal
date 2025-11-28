
from datetime import datetime, date
from sqlalchemy.orm import validates
from .base import Model, db

class Setting(Model):
    __tablename__ = 'setting'

    balance = db.Column(db.Float, nullable=False)
    show_r = db.Column(db.Boolean, nullable=False, default=False)
    commission = db.Column(db.Float, default=1.0)
    timezone = db.Column(db.String, default='UTC') # UTC, America/New_York, Europe/Madrid
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='settings')

    def toggle_r(self) -> None:
        self.show_r: bool = not self.show_r
        db.session.commit()
        
    def to_dict(self, exclude:list=[]):
        return {
            'balance': self.balance,
            'show_r': self.show_r,
            'commission': self.commission,
            'timezone': self.timezone,
            'user': {} if 'user' in exclude else self.user.to_dict(exclude=['settings']+exclude),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class Risk(Model):
    # Hay que modificar el journal para que se vea en r y no en dinero
    # Hay que modificar la página de performance
    # Hay que modificar la página de trade details
    # Hay que modificar la página de errores
    # Hay que modificar watchlist performance
    __tablename__ = 'risk'

    risk = db.Column(db.Float, nullable=False, default=1)
    date = db.Column(db.Date, nullable=False, default=date.today)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='risks')
    
    @validates('risk')
    def validate_risk(self, key, value):
        if value == 0:
            raise ValueError("The risk value can't be 0, it must be greater.")
        if value is None:
            raise ValueError("The risk value can't be None, it must be a float greater than 0.")
        return value
    
    def to_dict(self, exclude:list=[]):
        return {
            'risk': self.risk,
            'user': {} if 'user' in exclude else self.user.to_dict(exclude=['risks']+exclude),
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def getByDate(cls, target_date:str|datetime, user_id:int):
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
        
        # Buscar el Risk con fecha <= target_date, ordenado descendente
        return cls.query.filter(
            cls.user_id == user_id,
            cls.date <= target_date
        ).order_by(cls.date.desc()).first()