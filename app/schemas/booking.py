from datetime import datetime

from pydantic import BaseModel, Field

from app.models.booking import BookingStatus
from app.schemas.customer import CustomerInBooking


class BookingCreate(BaseModel):
    staff_id: int
    service_id: int
    start_at: datetime
    confirm: bool = Field(
        default=False,
        description="True → CONFIRMED сразу, False → HOLD на 10 минут",
    )
    customer: CustomerInBooking
    comment: str | None = None


class BookingRead(BaseModel):
    id: int
    business_id: int
    staff_id: int
    staff_service_id: int
    customer_id: int
    start_at: datetime
    end_at: datetime
    price: int
    duration_min: int
    status: BookingStatus
    expires_at: datetime | None
    customer_name: str | None
    comment: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class BookingConfirm(BaseModel):
    """Тело запроса для подтверждения HOLD-бронирования."""
    pass


class BookingCancel(BaseModel):
    """Тело запроса для отмены бронирования (расширяемо — reason и т.д.)."""
    reason: str | None = None
