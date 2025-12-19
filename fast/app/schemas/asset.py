"""
Schemas para Asset
"""

from pydantic import BaseModel
from typing import Optional


class AssetBase(BaseModel):
    symbol: str
    company_name: Optional[str] = None
    description: Optional[str] = None
    exchange: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    symbol: Optional[str] = None
    company_name: Optional[str] = None
    description: Optional[str] = None
    exchange: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None


class AssetResponse(AssetBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
