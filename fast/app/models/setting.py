"""
Modelo Setting
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import BaseModel


class Setting(BaseModel):
    """Configuración personalizada del usuario"""
    __tablename__ = "settings"
    
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    
    # Key-value pairs
    balance = Column(Float, nullable=False)
    show_r = Column(Boolean, nullable=False, default=False)
    commission = Column(Float, default=1.0)
    timezone = Column(String, default='UTC') # UTC, America/New_York, Europe/Madrid
    
    # Relaciones
    user = relationship("User", back_populates="settings_rel")

    def toggle_r(self) -> None:
        self.show_r: bool = not self.show_r
        db.session.commit()
