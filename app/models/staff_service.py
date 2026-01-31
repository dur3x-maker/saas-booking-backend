from sqlalchemy import (
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StaffService(Base):
    __tablename__ = "staff_services"

    id: Mapped[int] = mapped_column(primary_key=True)

    staff_id: Mapped[int] = mapped_column(
        ForeignKey("staff.id"),
        nullable=False,
        index=True,
    )

    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id"),
        nullable=False,
        index=True,
    )

    price: Mapped[int] = mapped_column(nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    staff = relationship("Staff", back_populates="staff_services")
    service = relationship("Service", back_populates="staff_services")

    bookings = relationship(
        "Booking",
        back_populates="staff_service",
    )

    __table_args__ = (
        UniqueConstraint(
            "staff_id",
            "service_id",
            name="uq_staff_service",
        ),
    )
