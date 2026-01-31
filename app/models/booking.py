import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Enum, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BookingStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
    no_show = "no_show"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)

    staff_id: Mapped[int] = mapped_column(
        ForeignKey("staff.id"),
        nullable=False,
        index=True,
    )

    staff_service_id: Mapped[int] = mapped_column(
        ForeignKey("staff_services.id"),
        nullable=False,
        index=True,
    )

    start_dt: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_dt: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # фиксируем состояние услуги на момент бронирования
    price: Mapped[int] = mapped_column(nullable=False)
    duration_min: Mapped[int] = mapped_column(nullable=False)

    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus),
        default=BookingStatus.pending,
        nullable=False,
    )

    customer_name: Mapped[str | None] = mapped_column(String, nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(String, nullable=True)
    comment: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    staff: Mapped["Staff"] = relationship(back_populates="bookings")
    staff_service: Mapped["StaffService"] = relationship(back_populates="bookings")
