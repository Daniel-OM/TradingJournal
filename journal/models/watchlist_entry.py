
from datetime import date, datetime, timezone
from sqlalchemy import and_

from .base import Model, db
from .watchlist_condition import WatchlistCondition
from .level import Level, watchlist_levels

watchlist_scoring = db.Table('watchlist_scoring',
    db.Column('watchlist_entry_id', db.Integer, db.ForeignKey('watchlist_entry.id'), primary_key=True),
    db.Column('condition_id', db.Integer, db.ForeignKey('watchlist_condition.id'), primary_key=True),
    db.Column('value', db.Float, default=0.0),
    db.Column('created_at', db.DateTime, default=datetime.now(timezone.utc))
)

class WatchlistEntry(Model):
    __tablename__ = 'watchlist_entry'

    date = db.Column(db.Date, nullable=False, default=date.today)
    symbol = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(200))
    atr = db.Column(db.Float)
    volume = db.Column(db.Float)
    avg_volume = db.Column(db.Float)
    price = db.Column(db.Float)
    score = db.Column(db.Float, nullable=False, default=0.0)
    description = db.Column(db.Text)
    negative_action = db.Column(db.Text)
    hashtags = db.Column(db.String(500)) # TODO: Define table for hashtags?
    risk_reward = db.Column(db.String(20))
    profit_target = db.Column(db.Float)
    other_notes = db.Column(db.Text)
    date_exit = db.Column(db.Date, nullable=True)
    watchlist_id = db.Column(db.Integer, db.ForeignKey('watchlist.id'))
    
    watchlist = db.relationship('Watchlist', back_populates='entries')
    levels = db.relationship('Level', secondary='watchlist_levels', back_populates='entries')
    conditions = db.relationship('WatchlistCondition', secondary='watchlist_scoring', back_populates='entries')
    
    def to_dict(self, exclude:list=[]):
        return {
            'id': self.id,
            'date': self.date,
            'symbol': self.symbol,
            'company_name': self.company_name,
            'atr': self.atr,
            'volume': self.volume,
            'avg_volume': self.avg_volume,
            'price': self.price,
            'score': self.score,
            'description': self.description,
            'negative_action': self.negative_action,
            'hashtags': self.hashtags,
            'risk_reward': self.risk_reward,
            'profit_target': self.profit_target,
            'other_notes': self.other_notes,
            'date_exit': self.date_exit,
            'performance': self.performance.to_dict(),
            'watchlist': {} if 'watchlist' in exclude else self.watchlist.to_dict(exclude=['entries']+exclude),
            'levels': [] if 'levels' in exclude else [l.to_dict(exclude=['entries']+exclude) for l in self.levels],
            'conditions': [] if 'conditions' in exclude else [l.to_dict(exclude=['entries', 'watchlist']+exclude) for l in self.conditions],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def add_level(self, price, date, impact_level='medium'):
        """Agregar un level a este trade"""
        # Buscar o crear el level
        level = Level.query.filter_by(symbol=self.symbol, price=price).first()
        if not level:
            level = Level(
                symbol=self.symbol,
                price=price,
                date=date
            )
            db.session.add(level)
            db.session.flush([level])
            
        # Verificar si la relación ya existe
        levels = db.session.execute(
            watchlist_levels.select().where(
                and_(watchlist_levels.c.watchlist_entry_id == self.id, 
                        watchlist_levels.c.level_id == level.id)
            )
        ).first()
        
        if not levels:
            # Actualizar el nivel de impacto en la tabla de asociación si es necesario
            db.session.execute(
                watchlist_levels.insert().values(
                    watchlist_entry_id=self.id,
                    level_id=level.id,
                    impact_level=impact_level
                )
            )

        db.session.commit()
    
    def remove_levels(self):
        """Remover un level de este trade"""
        for level in self.levels:
            # Actualizar el nivel de impacto en la tabla de asociación si es necesario
            db.session.execute(
                watchlist_levels.delete().where(and_(watchlist_levels.c.level_id == level.id, watchlist_levels.c.watchlist_entry_id == self.id))
            )
            
        db.session.commit()
    
    def _determine_severity(self, impact_level):
        """Determinar severidad basada en el nivel de impacto"""
        mapping = {
            'low': 'low',
            'medium': 'medium', 
            'high': 'high'
        }
        return mapping.get(impact_level, 'medium')
    
    def add_condition(self, condition_id:int, value:float):
        condition = WatchlistCondition.query.filter_by(id=condition_id).first()
        
        # Verificar si la relación ya existe
        if condition not in self.conditions:
            try:
                self.conditions.append(condition)
            except:    
                # Actualizar el nivel de impacto en la tabla de asociación si es necesario
                db.session.execute(
                    watchlist_scoring.insert().values(
                        watchlist_entry_id=self.id,
                        condition_id=condition_id,
                        value=value,
                    )
                )

        db.session.commit()

    def remove_conditions(self):
        for condition in self.conditions:
            # Actualizar el nivel de impacto en la tabla de asociación si es necesario
            db.session.execute(
                watchlist_scoring.delete().where(and_(watchlist_scoring.c.condition_id == condition.id, watchlist_scoring.c.watchlist_entry_id == self.id))
            )
        
        db.session.commit()

    @property
    def level_prices(self):
        """Lista de descripciones de levels para este trade"""
        return [level.price for level in self.levels]
    
    def delete_watchlist(self):
        self.date_exit = date.today()