from dataclasses import dataclass
from datetime import datetime, time, date

from app.services.availability_service import AvailabilityService


# ===== fakes (замена ORM моделей) =====

@dataclass
class WorkingHoursFake:
    staff_id: int
    weekday: int
    start_time: time
    end_time: time
    is_active: bool = True


@dataclass
class TimeOffFake:
    staff_id: int
    start_at: datetime
    end_at: datetime
    is_active: bool = True


@dataclass
class BookingFake:
    staff_id: int
    start_at: datetime
    end_at: datetime
    status: str
    is_active: bool = True


# ===== tests =====

def test_simple_day_availability():
    service = AvailabilityService(slot_step_minutes=30)
    day = date(2026, 2, 1)

    working_hours = [
        WorkingHoursFake(
            staff_id=1,
            weekday=day.weekday(),
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
    ]

    slots = service.get_slots_for_day(
        target_day=day,
        staff_id=1,
        service_duration_minutes=30,
        working_hours=working_hours,
        time_off=[],
        bookings=[],
    )

    assert len(slots) == 4
    assert slots[0].start == datetime(2026, 2, 1, 10, 0)
    assert slots[-1].end == datetime(2026, 2, 1, 12, 0)


def test_booking_blocks_middle():
    service = AvailabilityService(slot_step_minutes=30)
    day = date(2026, 2, 1)

    working_hours = [
        WorkingHoursFake(1, day.weekday(), time(10, 0), time(13, 0))
    ]

    bookings = [
        BookingFake(
            staff_id=1,
            start_at=datetime(2026, 2, 1, 11, 0),
            end_at=datetime(2026, 2, 1, 12, 0),
            status="confirmed",
        )
    ]

    slots = service.get_slots_for_day(
        target_day=day,
        staff_id=1,
        service_duration_minutes=30,
        working_hours=working_hours,
        time_off=[],
        bookings=bookings,
    )

    times = [(s.start.hour, s.start.minute) for s in slots]

    assert (11, 0) not in times
    assert (11, 30) not in times


def test_time_off_blocks_partially():
    service = AvailabilityService(slot_step_minutes=30)
    day = date(2026, 2, 1)

    working_hours = [
        WorkingHoursFake(1, day.weekday(), time(9, 0), time(12, 0))
    ]

    time_off = [
        TimeOffFake(
            staff_id=1,
            start_at=datetime(2026, 2, 1, 9, 30),
            end_at=datetime(2026, 2, 1, 10, 30),
        )
    ]

    slots = service.get_slots_for_day(
        target_day=day,
        staff_id=1,
        service_duration_minutes=30,
        working_hours=working_hours,
        time_off=time_off,
        bookings=[],
    )

    times = [(s.start.hour, s.start.minute) for s in slots]

    assert (9, 30) not in times
    assert (10, 0) not in times
