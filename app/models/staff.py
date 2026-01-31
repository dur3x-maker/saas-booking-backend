from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Table,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


from app.db.base import Base


# =========================
# Association table (NEW)
# =========================
staff_services = Table(
    "staff_services",
    Base.metadata,
    Column(
        "staff_id",
        Integer,
        ForeignKey("staff.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "service_id",
        Integer,
        ForeignKey("services.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)

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

services = relationship(
        "Service",
        secondary=staff_services,
        back_populates="staff",
        lazy="selectin",
    )

