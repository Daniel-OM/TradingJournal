
from .base import Model, db

class StrategyCondition(Model):
    __tablename__ = 'strategy_condition'

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    score = db.Column(db.Integer, default=10)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'), nullable=False)

    strategy = db.relationship('Strategy', back_populates='conditions')
    trades = db.relationship('Trade', secondary='trade_scoring', back_populates='conditions')
    
    def to_dict(self, exclude:list=[]):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'score': self.score,
            'strategy': {} if 'strategy' in exclude else self.strategy.to_dict(exclude=['conditions']+exclude),
            'trades': [] if 'trades' in exclude else [t.to_dict(exclude=['conditions']+exclude) for t in self.trades],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }