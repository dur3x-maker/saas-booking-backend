from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, DateTime
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

    business_users = relationship(
        "BusinessUser",
        back_populates="business",
        cascade="all, delete-orphan",
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

    customers = relationship(
        "Customer",
        back_populates="business",
        cascade="all, delete-orphan",
    )
