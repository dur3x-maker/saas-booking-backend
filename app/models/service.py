# app/models/service.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.staff import staff_services


from app.db.base import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)

    duration_minutes = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    staff = relationship(
        "Staff",
        secondary=staff_services,
        back_populates="services",
        lazy="selectin",
    )
