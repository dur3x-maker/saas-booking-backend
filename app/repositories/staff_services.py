# app/repositories/staff_services.py

from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.staff_service import StaffService


def get_for_staff(
    session: Session,
    *,
    staff_id: int,
) -> List[StaffService]:
    """
    Возвращает все активные StaffService для сотрудника.
    """
    stmt = (
        select(StaffService)
        .where(
            StaffService.staff_id == staff_id,
            StaffService.is_active == True,
        )
    )

    return list(session.scalars(stmt))
