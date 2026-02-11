from datetime import datetime
from pydantic import BaseModel, Field


class StaffBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str | None = Field(None, max_length=100)

    phone: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=255)

    is_active: bool = True


class StaffCreate(StaffBase):
    pass


class StaffUpdate(BaseModel):
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)

    phone: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=255)

    is_active: bool | None = None


class StaffRead(StaffBase):
    id: int
    business_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
