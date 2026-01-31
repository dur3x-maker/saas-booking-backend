from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class StaffService(Base):
    __tablename__ = "staff_services"

    staff_id = Column(
        Integer,
        ForeignKey("staff.id", ondelete="CASCADE"),
        primary_key=True,
    )
    service_id = Column(
        Integer,
        ForeignKey("services.id", ondelete="CASCADE"),
        primary_key=True,
    )

    price = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    staff = relationship("Staff", back_populates="staff_services")
    service = relationship("Service", back_populates="staff_services")
