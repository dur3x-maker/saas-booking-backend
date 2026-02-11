# app/api/v1/schedule.py

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.schedule_service import ScheduleService
from app.services.booking_service import SLOT_STEP_MINUTES, BOOKING_HORIZON_DAYS

router = APIRouter(tags=["Schedule"])


@router.get("/schedule/staff/{staff_id}/slots")
def get_staff_slots(
    business_id: int,
    staff_id: int,
    service_id: int = Query(..., description="Service ID"),
    day: date = Query(..., description="Target day (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    now = datetime.utcnow()
    today = now.date()

    # Прошедшие дни → 400
    if day < today:
        raise HTTPException(
            status_code=400,
            detail="Нельзя запросить слоты за прошедший день",
        )

    # Горизонт → 400
    horizon_date = (now + timedelta(days=BOOKING_HORIZON_DAYS)).date()
    if day > horizon_date:
        raise HTTPException(
            status_code=400,
            detail=f"Горизонт бронирования — не дальше {BOOKING_HORIZON_DAYS} дней вперёд",
        )

    schedule_service = ScheduleService(slot_step_minutes=SLOT_STEP_MINUTES)

    try:
        slots = schedule_service.get_slots_for_day(
            session=db,
            business_id=business_id,
            staff_id=staff_id,
            service_id=service_id,
            day=day,
            now=now,
        )
    except LookupError as e:
        # например, если StaffService не найден
        raise HTTPException(status_code=404, detail=str(e))

    return [
        {
            "start": slot.start,
            "end": slot.end,
        }
        for slot in slots
    ]
