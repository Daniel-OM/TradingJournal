
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db: SQLAlchemy = SQLAlchemy()
migrate: Migrate = Migrate()

# Modelos de la Base de Datos
class Model(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))