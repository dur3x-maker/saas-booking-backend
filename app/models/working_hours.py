from datetime import time

from sqlalchemy import (
    Integer, Time, Boolean, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class WorkingHours(Base):
    __tablename__ = "working_hours"

    id: Mapped[int] = mapped_column(primary_key=True)

    staff_id: Mapped[int] = mapped_column(
        ForeignKey("staff.id"),
        nullable=False,
        index=True,
    )

    weekday: Mapped[int] = mapped_column(nullable=False)  # 0=Mon .. 6=Sun

    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    break_start: Mapped[time | None] = mapped_column(Time, nullable=True)
    break_end: Mapped[time | None] = mapped_column(Time, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    staff: Mapped["Staff"] = relationship(back_populates="working_hours")

    __table_args__ = (
        UniqueConstraint("staff_id", "weekday", name="uq_staff_weekday"),
    )
