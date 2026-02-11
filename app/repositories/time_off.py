# app/repositories/time_off.py

from typing import List
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.time_off import TimeOff


def get_for_staff_and_period(
    session: Session,
    *,
    staff_id: int,
    start: datetime,
    end: datetime,
) -> List[TimeOff]:
    """
    Возвращает все TimeOff сотрудника, которые
    пересекаются с периодом [start, end).

    Пересечение:
        time_off.start_at < end AND time_off.end_at > start
    """
    stmt = (
        select(TimeOff)
        .where(
            TimeOff.staff_id == staff_id,
            TimeOff.is_active == True,
            TimeOff.start_at < end,
            TimeOff.end_at > start,
        )
        .order_by(TimeOff.start_at.asc())
    )

    return list(session.scalars(stmt))
