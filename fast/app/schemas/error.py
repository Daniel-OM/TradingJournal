"""
Schemas para Error
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ErrorBase(BaseModel):
    description: str
    category: Optional[str] = None
    severity: Optional[str] = None
    is_active: bool = True


class ErrorCreate(ErrorBase):
    pass


class ErrorUpdate(BaseModel):
    description: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    is_active: Optional[bool] = None


class ErrorResponse(ErrorBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
