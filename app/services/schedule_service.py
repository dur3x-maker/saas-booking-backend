# app/services/schedule_service.py

from datetime import date, datetime, time, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from app.repositories import (
    working_hours as working_hours_repo,
    time_off as time_off_repo,
    bookings as bookings_repo,
    staff_services as staff_services_repo,
)
from app.models.staff import Staff
from app.services.availability_service import AvailabilityService
from app.services.availability_service import Slot
from app.services.booking_service import (
    BOOKING_HORIZON_DAYS,
    MIN_LEAD_TIME_MINUTES,
)


class ScheduleService:
    """
    Application service.

    Отвечает за сценарий:
    «Получить доступные слоты для сотрудника под услугу на день».
    """

    def __init__(self, *, slot_step_minutes: int = 15) -> None:
        self._availability = AvailabilityService(
            slot_step_minutes=slot_step_minutes
        )

    def get_slots_for_day(
        self,
        *,
        session: Session,
        business_id: int,
        staff_id: int,
        service_id: int,
        day: date,
        now: Optional[datetime] = None,
    ) -> List[Slot]:
        """
        Возвращает список слотов для записи.

        now:
            если передан — слоты в прошлом и ближе lead time
            будут отброшены (удобно для "сегодня").

        Если day за пределами горизонта — возвращает пустой список.
        """
        # Горизонт: дни за пределами BOOKING_HORIZON_DAYS → пустой список
        if now is not None:
            horizon_date = (now + timedelta(days=BOOKING_HORIZON_DAYS)).date()
            if day > horizon_date:
                return []

        # Lead time: сдвигаем "now" вперёд, чтобы AvailabilityService
        # отрезал слоты, которые нельзя забронировать по lead time
        effective_now = None
        if now is not None:
            effective_now = now + timedelta(minutes=MIN_LEAD_TIME_MINUTES)

        day_start = datetime.combine(day, time.min)
        day_end = day_start + timedelta(days=1)

        # Проверка принадлежности staff к business
        staff = session.get(Staff, staff_id)
        if staff is None or staff.business_id != business_id:
            raise LookupError(
                f"Staff {staff_id} not found in business {business_id}"
            )

        # 1️⃣ Данные из БД (repositories)
        working_hours = working_hours_repo.get_for_staff_and_weekday(
            session=session,
            staff_id=staff_id,
            weekday=day.weekday(),
        )

        time_off = time_off_repo.get_for_staff_and_period(
            session=session,
            staff_id=staff_id,
            start=day_start,
            end=day_end,
        )

        bookings = bookings_repo.get_blocking_for_staff_and_period(
            session=session,
            staff_id=staff_id,
            start=day_start,
            end=day_end,
            business_id=business_id,
        )

        staff_services = staff_services_repo.get_for_staff(
            session=session,
            staff_id=staff_id,
        )

        # 2️⃣ Длительность услуги (доменное правило)
        service_duration_minutes = resolve_service_duration_minutes(
            staff_id=staff_id,
            service_id=service_id,
            staff_services=staff_services,
        )

        # 3️⃣ Расчёт слотов (чистая бизнес-логика)
        slots = self._availability.get_slots_for_day(
            target_day=day,
            staff_id=staff_id,
            service_duration_minutes=service_duration_minutes,
            working_hours=working_hours,
            time_off=time_off,
            bookings=bookings,
            now=effective_now,
        )

        return slots
    
def resolve_service_duration_minutes(
    *,
    staff_id: int,
    service_id: int,
    staff_services,
    ) -> int:
        """
        Возвращает длительность услуги для сотрудника
        на основе StaffService.
        """
        for ss in staff_services:
            if getattr(ss, "is_active", True) is False:
                continue
            if ss.staff_id == staff_id and ss.service_id == service_id:
                if ss.duration <= 0:
                    raise ValueError("StaffService.duration must be > 0")
                return int(ss.duration)

        raise LookupError(
            f"StaffService not found for staff_id={staff_id}, service_id={service_id}"
        )

