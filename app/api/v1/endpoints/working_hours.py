from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_business, BusinessContext
from app.models.working_hours import WorkingHours
from app.schemas.working_hours import (
    WorkingHoursCreate,
    WorkingHoursRead,
)
from app.repositories import working_hours as repo


router = APIRouter(tags=["Working Hours"])


@router.post(
    "/working-hours",
    response_model=WorkingHoursRead,
    status_code=201,
)
def create_working_hours(
    payload: WorkingHoursCreate,
    session: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    wh = WorkingHours(**payload.dict(), business_id=ctx.business_id)
    return repo.create(session=session, wh=wh)


@router.get(
    "/working-hours",
    response_model=list[WorkingHoursRead],
)
def list_working_hours(
    staff_id: int,
    session: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    return (
        session.query(WorkingHours)
        .filter(
            WorkingHours.staff_id == staff_id,
            WorkingHours.business_id == ctx.business_id,
        )
        .order_by(WorkingHours.weekday, WorkingHours.start_time)
        .all()
    )
