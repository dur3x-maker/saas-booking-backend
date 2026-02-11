import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Enum, String, Integer, Boolean, Index, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BookingStatus(enum.Enum):
    """
    HOLD      — временная бронь, ожидает подтверждения (expires_at задан)
    CONFIRMED — подтверждённая бронь
    CANCELLED — отменённая бронь (не блокирует слоты)
    EXPIRED   — HOLD, у которого истёк expires_at (не блокирует слоты)
    """
    HOLD = "hold"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


# Статусы, которые блокируют временной слот сотрудника
BLOCKING_STATUSES = (BookingStatus.HOLD, BookingStatus.CONFIRMED)


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)

    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id"),
        nullable=False,
        index=True,
    )

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

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    start_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    # snapshot — фиксируем состояние услуги на момент бронирования
    price: Mapped[int] = mapped_column(nullable=False)
    duration_min: Mapped[int] = mapped_column(nullable=False)

    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, values_callable=lambda x: [e.value for e in x]),
        default=BookingStatus.HOLD,
        nullable=False,
    )

    # для HOLD-бронирований: время, после которого бронь считается истёкшей
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    customer_name: Mapped[str | None] = mapped_column(String, nullable=True)
    comment: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    business: Mapped["Business"] = relationship(back_populates="bookings")
    staff: Mapped["Staff"] = relationship(back_populates="bookings")
    staff_service: Mapped["StaffService"] = relationship(back_populates="bookings")
    customer: Mapped["Customer"] = relationship(back_populates="bookings")

    __table_args__ = (
        # Составной индекс для быстрого поиска пересечений по сотруднику
        Index(
            "ix_bookings_staff_overlap",
            "staff_id",
            "start_at",
            "end_at",
            "status",
        ),
    )
