# app/repositories/working_hours.py

from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.working_hours import WorkingHours


def create(session: Session, wh: WorkingHours) -> WorkingHours:
    session.add(wh)
    session.commit()
    session.refresh(wh)
    return wh

def get_for_staff_and_weekday(
    session: Session,
    *,
    staff_id: int,
    weekday: int,
) -> List[WorkingHours]:
    """
    Возвращает рабочие часы сотрудника на конкретный день недели.

    weekday:
        0 = Monday
        6 = Sunday
    """
    stmt = (
        select(WorkingHours)
        .where(
            WorkingHours.staff_id == staff_id,
            WorkingHours.weekday == weekday,
            WorkingHours.is_active == True,
        )
        .order_by(WorkingHours.start_time.asc())
    )

    return list(session.scalars(stmt))
