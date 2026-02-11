# app/repositories/bookings.py

from typing import List, Optional, Sequence
from datetime import datetime

from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus, BLOCKING_STATUSES


def get_blocking_for_staff_and_period(
    session: Session,
    *,
    staff_id: int,
    start: datetime,
    end: datetime,
    business_id: Optional[int] = None,
) -> List[Booking]:
    """
    Возвращает брони сотрудника, которые:
    - пересекаются с периодом [start, end)
    - имеют блокирующий статус (HOLD с не-истёкшим expires_at, или CONFIRMED)

    Пересечение:
        booking.start_at < end AND booking.end_at > start
    """
    now = datetime.utcnow()
    conditions = [
        Booking.staff_id == staff_id,
        Booking.is_active == True,
    ]
    if business_id is not None:
        conditions.append(Booking.business_id == business_id)
    stmt = (
        select(Booking)
        .where(
            *conditions,
            Booking.start_at < end,
            Booking.end_at > start,
            or_(
                Booking.status == BookingStatus.CONFIRMED,
                and_(
                    Booking.status == BookingStatus.HOLD,
                    Booking.expires_at > now,
                ),
            ),
        )
        .order_by(Booking.start_at.asc())
    )

    return list(session.scalars(stmt))


def has_overlap(
    session: Session,
    *,
    staff_id: int,
    start_at: datetime,
    end_at: datetime,
    exclude_booking_id: Optional[int] = None,
    business_id: Optional[int] = None,
) -> bool:
    """
    Проверяет наличие пересечений с существующими блокирующими бронями.
    Учитывает CONFIRMED и HOLD (если expires_at > now).
    """
    now = datetime.utcnow()
    conditions = [
        Booking.staff_id == staff_id,
        Booking.is_active == True,
        Booking.start_at < end_at,
        Booking.end_at > start_at,
        or_(
            Booking.status == BookingStatus.CONFIRMED,
            and_(
                Booking.status == BookingStatus.HOLD,
                Booking.expires_at > now,
            ),
        ),
    ]

    if exclude_booking_id is not None:
        conditions.append(Booking.id != exclude_booking_id)
    if business_id is not None:
        conditions.append(Booking.business_id == business_id)

    stmt = select(Booking.id).where(*conditions).limit(1)
    return session.scalar(stmt) is not None


def get_by_id(
    session: Session,
    booking_id: int,
    *,
    business_id: Optional[int] = None,
) -> Optional[Booking]:
    """Получает бронирование по ID. Если передан business_id — проверяет принадлежность."""
    booking = session.get(Booking, booking_id)
    if booking is not None and business_id is not None:
        if booking.business_id != business_id:
            return None
    return booking


def create(session: Session, booking: Booking) -> Booking:
    session.add(booking)
    session.flush()  # flush, не commit — commit делает вызывающий код
    return booking
