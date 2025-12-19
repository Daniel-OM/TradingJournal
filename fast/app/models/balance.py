"""
Modelo para AccountBalance (Saldo de Cuenta)
"""
from datetime import date, datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import BaseModel


class AccountBalance(BaseModel):
    """Modelo de Saldo de Cuenta por fecha"""
    __tablename__ = "account_balance"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    balance = Column(Float, nullable=False)
    daily_return = Column(Float, default=0.0)

    # Relationship
    user = relationship("User", back_populates="account_balances")
