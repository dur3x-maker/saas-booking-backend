from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    timezone = Column(String, default="UTC")
    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    owner = relationship(
        "User",
        foreign_keys=[owner_id],
    )

    users = relationship(
        "User",
        back_populates="business",
        foreign_keys="User.business_id",
    )

    staff = relationship(
        "Staff",
        back_populates="business",
        cascade="all, delete-orphan",
    )

    services = relationship(
        "Service",
        back_populates="business",
        cascade="all, delete-orphan",
    )

    bookings = relationship(
        "Booking",
        back_populates="business",
        cascade="all, delete-orphan",
    )

    working_hours = relationship(
        "WorkingHours",
        back_populates="business",
        cascade="all, delete-orphan",
    )

    time_off = relationship(
        "TimeOff",
        back_populates="business",
        cascade="all, delete-orphan",
    )
