from datetime import datetime

from pydantic import BaseModel


class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: str | None = None


class CustomerRead(BaseModel):
    id: int
    business_id: int
    name: str
    phone: str
    email: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CustomerInBooking(BaseModel):
    """Вложенный объект customer внутри BookingCreate."""
    name: str
    phone: str
    email: str | None = None
