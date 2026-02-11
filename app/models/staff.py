from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


from app.db.base import Base


class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)

    business_id = Column(
        Integer,
        ForeignKey("businesses.id"),
        nullable=False,
        index=True,
    )

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)

    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    business = relationship("Business", back_populates="staff")

    staff_services = relationship(
        "StaffService",
        back_populates="staff",
        cascade="all, delete-orphan",
    )
    working_hours = relationship(
        "WorkingHours",
        back_populates="staff",
        cascade="all, delete-orphan",
    )

    time_off = relationship(
        "TimeOff",
        back_populates="staff",
        cascade="all, delete-orphan",
    )
    bookings = relationship(
        "Booking",
        back_populates="staff",
        cascade="all, delete-orphan",
    )
