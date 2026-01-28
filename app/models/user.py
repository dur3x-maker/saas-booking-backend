from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    role = Column(String, default="owner")
    is_active = Column(Boolean, default=True)

    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=True)

    business = relationship(
        "Business",
        foreign_keys=[business_id],
        back_populates="users",
    )
