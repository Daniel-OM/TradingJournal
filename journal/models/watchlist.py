
from datetime import datetime, timezone

from .base import Model, db
from .watchlist_condition import WatchlistCondition

class Watchlist(Model):
    __tablename__ = 'watchlist'

    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String, nullable=False) # SCALP, DAY, SWING, INVEST
    description = db.Column(db.Text)
    
    conditions = db.relationship('WatchlistCondition', back_populates='watchlist')
    entries = db.relationship('WatchlistEntry', back_populates='watchlist')
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='watchlists')
    
    def to_dict(self, exclude:list=[]):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'conditions': [] if 'conditions' in exclude else [c.to_dict(exclude=['watchlist']+exclude) for c in self.conditions],
            'entries': [] if 'entries' in exclude else [c.to_dict(exclude=['watchlist']+exclude) for c in self.entries],
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def add_condition(self, name:str, description:str, score:float):
        """Agregar un level a este trade"""
        # Buscar o crear el level
        entity = WatchlistCondition.query.filter_by(name=name, description=description, score=score, watchlist_id=self.id).first()
        if not entity:
            entity = WatchlistCondition(
                name=name,
                description=description,
                score=float(score),
                watchlist_id=self.id
            )
            db.session.add(entity)
    
    def remove_condition(self, name:str, description:str, score:float):
        """Remover un level de este trade"""
        entity = WatchlistCondition.query.filter_by(name=name, description=description, score=score, watchlist_id=self.id).first()
        if entity: db.session.delete(entity)