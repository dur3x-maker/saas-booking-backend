import enum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base


class BusinessRole(enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"


class BusinessUser(Base):
    __tablename__ = "business_users"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    business_id = Column(
        Integer,
        ForeignKey("businesses.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    role = Column(
        Enum(BusinessRole, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=BusinessRole.ADMIN,
    )

    user = relationship("User", back_populates="business_users")
    business = relationship("Business", back_populates="business_users")
