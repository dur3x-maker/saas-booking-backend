

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Iterable, List, Optional, Protocol, Sequence, Tuple


# ============================================================
# Public DTOs (то, что можно отдавать наружу — в API позже)
# ============================================================

@dataclass(frozen=True)
class TimeRange:
    """
    Полуинтервал [start, end) в локальном времени (naive datetime).
    Конвенция полуинтервала упрощает математику: end не включаем.
    """
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError("TimeRange end must be > start")


@dataclass(frozen=True)
class Slot:
    """
    Слот под услугу: [start, end)
    """
    start: datetime
    end: datetime


# ============================================================
# Minimal contracts (Protocol) — сервис не зависит от ORM
# ============================================================

class WorkingHoursLike(Protocol):
    staff_id: int
    weekday: int  # 0=Mon ... 6=Sun
    start_time: time
    end_time: time
    is_active: bool


class TimeOffLike(Protocol):
    staff_id: int
    start_at: datetime
    end_at: datetime
    is_active: bool


class BookingLike(Protocol):
    staff_id: int
    start_at: datetime
    end_at: datetime
    status: str  # например: "confirmed", "cancelled"
    is_active: bool  # если у тебя есть, супер; если нет — ставим всегда True


class StaffServiceLike(Protocol):
    staff_id: int
    service_id: int
    duration: int  # minutes
    is_active: bool


# ============================================================
# Core service
# ============================================================

class AvailabilityService:
    def __init__(self, slot_step_minutes: int = 15) -> None:
        if slot_step_minutes <= 0:
            raise ValueError("slot_step_minutes must be > 0")
        self._slot_step = timedelta(minutes=slot_step_minutes)

    # ---------- public ----------

    def get_available_ranges_for_day(
        self,
        *,
        target_day: date,
        staff_id: int,
        working_hours: Sequence[WorkingHoursLike],
        time_off: Sequence[TimeOffLike],
        bookings: Sequence[BookingLike],
        booking_block_statuses: Optional[Sequence[str]] = None,
        now: Optional[datetime] = None,
    ) -> List[TimeRange]:
        block_statuses = tuple(booking_block_statuses or ("confirmed", "hold"))

        day_work = self._working_ranges_for_day(
            target_day=target_day,
            staff_id=staff_id,
            working_hours=working_hours,
        )

        if not day_work:
            return []

        day_start = datetime.combine(target_day, time.min)
        day_end = day_start + timedelta(days=1)

        blocks: List[TimeRange] = []

        for t in time_off:
            if getattr(t, "is_active", True) is False:
                continue
            if t.staff_id != staff_id:
                continue
            blocks.extend(self._clip_to_day(
                TimeRange(t.start_at, t.end_at), day_start, day_end
            ))

        for b in bookings:
            if getattr(b, "is_active", True) is False:
                continue
            if b.staff_id != staff_id:
                continue
            b_status = b.status.value if hasattr(b.status, "value") else b.status
            if b_status not in block_statuses:
                continue
            blocks.extend(self._clip_to_day(
                TimeRange(b.start_at, b.end_at), day_start, day_end
            ))

        blocks = self._merge_ranges(blocks)

        available = day_work
        for block in blocks:
            available = self._subtract_many(available, block)

        if now is not None:
            available = self._cut_past(available, now)

        return self._merge_ranges(available)

    def get_slots_for_day(
        self,
        *,
        target_day: date,
        staff_id: int,
        service_duration_minutes: int,
        working_hours: Sequence[WorkingHoursLike],
        time_off: Sequence[TimeOffLike],
        bookings: Sequence[BookingLike],
        slot_step_minutes: Optional[int] = None,
        booking_block_statuses: Optional[Sequence[str]] = None,
        now: Optional[datetime] = None,
        align_to_work_start: bool = True,
    ) -> List[Slot]:
        step = timedelta(minutes=slot_step_minutes) if slot_step_minutes else self._slot_step
        duration = timedelta(minutes=service_duration_minutes)

        available_ranges = self.get_available_ranges_for_day(
            target_day=target_day,
            staff_id=staff_id,
            working_hours=working_hours,
            time_off=time_off,
            bookings=bookings,
            booking_block_statuses=booking_block_statuses,
            now=now,
        )

        slots: List[Slot] = []
        day_start = datetime.combine(target_day, time.min)

        for r in available_ranges:
            grid_anchor = r.start if align_to_work_start else day_start
            t = self._ceil_to_grid(r.start, grid_anchor, step)

            while t + duration <= r.end:
                slots.append(Slot(start=t, end=t + duration))
                t += step

        return slots

    # ---------- internals ----------

    def _working_ranges_for_day(self, *, target_day: date, staff_id: int,
                                working_hours: Sequence[WorkingHoursLike]) -> List[TimeRange]:
        wd = target_day.weekday()
        ranges: List[TimeRange] = []

        for wh in working_hours:
            if getattr(wh, "is_active", True) is False:
                continue
            if wh.staff_id != staff_id or wh.weekday != wd:
                continue

            start_dt = datetime.combine(target_day, wh.start_time)
            end_dt = datetime.combine(target_day, wh.end_time)
            if end_dt <= start_dt:
                end_dt += timedelta(days=1)

            break_start = getattr(wh, "break_start", None)
            break_end = getattr(wh, "break_end", None)

            if break_start and break_end:
                brk_start_dt = datetime.combine(target_day, break_start)
                brk_end_dt = datetime.combine(target_day, break_end)
                # Разбиваем рабочий диапазон на два: до и после перерыва
                if brk_start_dt > start_dt:
                    ranges.append(TimeRange(start=start_dt, end=brk_start_dt))
                if brk_end_dt < end_dt:
                    ranges.append(TimeRange(start=brk_end_dt, end=end_dt))
            else:
                ranges.append(TimeRange(start=start_dt, end=end_dt))

        return self._merge_ranges(ranges)

    @staticmethod
    def _merge_ranges(ranges: Sequence[TimeRange]) -> List[TimeRange]:
        if not ranges:
            return []
        sorted_ranges = sorted(ranges, key=lambda r: (r.start, r.end))
        merged = [sorted_ranges[0]]

        for cur in sorted_ranges[1:]:
            last = merged[-1]
            if cur.start <= last.end:
                merged[-1] = TimeRange(last.start, max(last.end, cur.end))
            else:
                merged.append(cur)
        return merged

    @staticmethod
    def _clip_to_day(r: TimeRange, day_start: datetime, day_end: datetime) -> List[TimeRange]:
        start = max(r.start, day_start)
        end = min(r.end, day_end)
        if end <= start:
            return []
        return [TimeRange(start=start, end=end)]

    @staticmethod
    def _ceil_to_grid(value: datetime, anchor: datetime, step: timedelta) -> datetime:
        if value <= anchor:
            return anchor
        delta = value - anchor
        seconds = int(delta.total_seconds())
        step_sec = int(step.total_seconds())
        k = (seconds + step_sec - 1) // step_sec
        return anchor + timedelta(seconds=k * step_sec)

    @staticmethod
    def _subtract_one(a: TimeRange, b: TimeRange) -> List[TimeRange]:
        if b.end <= a.start or b.start >= a.end:
            return [a]
        res = []
        if b.start > a.start:
            res.append(TimeRange(a.start, min(b.start, a.end)))
        if b.end < a.end:
            res.append(TimeRange(max(b.end, a.start), a.end))
        return res

    def _subtract_many(self, ranges: Sequence[TimeRange], block: TimeRange) -> List[TimeRange]:
        out: List[TimeRange] = []
        for r in ranges:
            out.extend(self._subtract_one(r, block))
        return self._merge_ranges(out)

    @staticmethod
    def _cut_past(ranges: Sequence[TimeRange], now: datetime) -> List[TimeRange]:
        out = []
        for r in ranges:
            if r.end <= now:
                continue
            if r.start < now < r.end:
                out.append(TimeRange(now, r.end))
            else:
                out.append(r)
        return out
