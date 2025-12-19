"""
Schemas para Setting
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SettingBase(BaseModel):
    key: str
    value: str


class SettingCreate(SettingBase):
    user_id: int


class SettingUpdate(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None


class SettingResponse(SettingBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
