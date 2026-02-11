# app/schemas/services.py

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class ServiceBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=1000)
    duration_minutes: int = Field(..., gt=0)
    price: Decimal = Field(..., ge=0)
    is_active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=1000)
    duration_minutes: int | None = Field(None, gt=0)
    price: Decimal | None = Field(None, ge=0)
    is_active: bool | None = None


class ServiceRead(ServiceBase):
    id: int
    business_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
