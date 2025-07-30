
from .base import Model, db
from .strategy_condition import StrategyCondition

class Strategy(Model):
    __tablename__ = 'strategy'

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    conditions = db.relationship('StrategyCondition', back_populates='strategy', cascade='all, delete-orphan', lazy='dynamic')
    trades = db.relationship('Trade', back_populates='strategy', cascade='all, delete-orphan', lazy='dynamic')
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='strategies')
    
    def to_dict(self, exclude:list=[]):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'trades': [] if 'trades' in exclude else [t.to_dict(exclude=['strategy']+exclude) for t in self.trades],
            'conditions': [] if 'conditions' in exclude else [c.to_dict(exclude=['strategy']+exclude) for c in self.conditions],
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def add_condition(self, name:str, description:str, score:float):
        """Agregar un level a este trade"""
        # Buscar o crear el level
        entity = StrategyCondition.query.filter_by(name=name, description=description, score=score, strategy_id=self.id).first()
        if not entity:
            entity = StrategyCondition(
                name=name,
                description=description,
                score=float(score),
                strategy_id=self.id
            )
            db.session.add(entity)
    
    def remove_condition(self, name:str, description:str, score:float):
        """Remover un level de este trade"""
        entity = StrategyCondition.query.filter_by(name=name, description=description, score=score, strategy_id=self.id).first()
        if entity: db.session.delete(entity)