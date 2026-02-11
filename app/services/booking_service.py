# app/services/booking_service.py

from __future__ import annotations

from datetime import datetime, timedelta, time
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.staff import Staff
from app.models.service import Service
from app.models.staff_service import StaffService
from app.models.working_hours import WorkingHours
from app.models.time_off import TimeOff
from app.models.customer import Customer
from app.repositories import (
    bookings as bookings_repo,
    staff_services as staff_services_repo,
    working_hours as working_hours_repo,
    time_off as time_off_repo,
    customers as customers_repo,
)

# HOLD живёт 10 минут
HOLD_TTL_MINUTES = 10

# Горизонт бронирования: максимум N дней вперёд
BOOKING_HORIZON_DAYS = 30

# Минимальное время до начала слота (lead time)
MIN_LEAD_TIME_MINUTES = 60

# Шаг сетки слотов (минуты). start_at должен быть кратен этому значению.
SLOT_STEP_MINUTES = 15


class BookingError(Exception):
    """Базовое исключение для ошибок бронирования."""
    pass


class SlotUnavailableError(BookingError):
    """Слот недоступен (пересечение, вне рабочих часов и т.д.)."""
    pass


class BookingNotFoundError(BookingError):
    """Бронирование не найдено."""
    pass


class BookingStateError(BookingError):
    """Некорректный переход статуса."""
    pass


class BookingService:
    """
    Сервисный слой для создания, подтверждения и отмены бронирований.

    Все мутирующие операции оборачиваются в BEGIN IMMEDIATE (SQLite)
    для предотвращения конкурентных записей.
    """

    # ------------------------------------------------------------------ #
    #  CREATE
    # ------------------------------------------------------------------ #

    def create_booking(
        self,
        session: Session,
        *,
        business_id: int,
        staff_id: int,
        service_id: int,
        start_at: datetime,
        confirm: bool = False,
        customer_name: str,
        customer_phone: str,
        customer_email: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> Booking:
        """
        Создаёт бронирование.

        1. Бизнес-правила (прошлое, горизонт, lead time, alignment,
           staff_service, рабочие часы, перерывы, time_off)
        2. BEGIN IMMEDIATE → проверка пересечений → INSERT → COMMIT
        """
        now = datetime.utcnow()

        # --- 1. Resolve staff_service (нужен для end_at) ---
        # Проверка принадлежности staff и service к business_id
        staff_service = self._resolve_staff_service(
            session,
            business_id=business_id,
            staff_id=staff_id,
            service_id=service_id,
        )

        duration_minutes = staff_service.duration
        price = staff_service.price
        end_at = start_at + timedelta(minutes=duration_minutes)

        # --- 2. Все бизнес-проверки (read-only, до BEGIN IMMEDIATE) ---
        self._validate_business_rules(
            session,
            now=now,
            staff_id=staff_id,
            start_at=start_at,
            end_at=end_at,
        )

        # --- 3. Get-or-create customer ---
        customer = customers_repo.get_by_phone(
            session, business_id=business_id, phone=customer_phone,
        )
        if customer is None:
            customer = Customer(
                business_id=business_id,
                name=customer_name,
                phone=customer_phone,
                email=customer_email,
            )
            customers_repo.create(session, customer)
        else:
            # Обновляем имя/email если переданы новые значения
            customer.name = customer_name
            if customer_email is not None:
                customer.email = customer_email

        # --- 4. Конкурентная запись: BEGIN IMMEDIATE ---
        self._begin_immediate(session)

        try:
            # Проверка пересечений внутри эксклюзивной транзакции
            if bookings_repo.has_overlap(
                session,
                staff_id=staff_id,
                start_at=start_at,
                end_at=end_at,
                business_id=business_id,
            ):
                raise SlotUnavailableError(
                    "Слот пересекается с существующим бронированием"
                )

            status = BookingStatus.CONFIRMED if confirm else BookingStatus.HOLD
            expires_at = (
                None if confirm
                else datetime.utcnow() + timedelta(minutes=HOLD_TTL_MINUTES)
            )

            booking = Booking(
                business_id=business_id,
                staff_id=staff_id,
                staff_service_id=staff_service.id,
                customer_id=customer.id,
                start_at=start_at,
                end_at=end_at,
                price=price,
                duration_min=duration_minutes,
                status=status,
                expires_at=expires_at,
                customer_name=customer_name,
                comment=comment,
            )

            bookings_repo.create(session, booking)
            session.commit()
            return booking

        except Exception:
            session.rollback()
            raise

    # ------------------------------------------------------------------ #
    #  CONFIRM
    # ------------------------------------------------------------------ #

    def confirm_booking(
        self, session: Session, booking_id: int, *, business_id: int,
    ) -> Booking:
        """
        Подтверждает HOLD-бронирование.
        Проверяет, что HOLD ещё не истёк.
        """
        booking = bookings_repo.get_by_id(
            session, booking_id, business_id=business_id,
        )
        if booking is None or not booking.is_active:
            raise BookingNotFoundError(f"Бронирование {booking_id} не найдено")

        if booking.status != BookingStatus.HOLD:
            raise BookingStateError(
                f"Нельзя подтвердить бронирование в статусе {booking.status.value}"
            )

        now = datetime.utcnow()
        if booking.expires_at is not None and booking.expires_at <= now:
            # Автоматически помечаем как EXPIRED
            booking.status = BookingStatus.EXPIRED
            session.commit()
            raise BookingStateError("HOLD истёк, бронирование переведено в EXPIRED")

        self._begin_immediate(session)
        try:
            booking.status = BookingStatus.CONFIRMED
            booking.expires_at = None
            session.commit()
            return booking
        except Exception:
            session.rollback()
            raise

    # ------------------------------------------------------------------ #
    #  CANCEL
    # ------------------------------------------------------------------ #

    def cancel_booking(
        self, session: Session, booking_id: int, *, business_id: int,
    ) -> Booking:
        """
        Отменяет бронирование (HOLD или CONFIRMED → CANCELLED).
        """
        booking = bookings_repo.get_by_id(
            session, booking_id, business_id=business_id,
        )
        if booking is None or not booking.is_active:
            raise BookingNotFoundError(f"Бронирование {booking_id} не найдено")

        if booking.status not in (BookingStatus.HOLD, BookingStatus.CONFIRMED):
            raise BookingStateError(
                f"Нельзя отменить бронирование в статусе {booking.status.value}"
            )

        self._begin_immediate(session)
        try:
            booking.status = BookingStatus.CANCELLED
            booking.expires_at = None
            session.commit()
            return booking
        except Exception:
            session.rollback()
            raise

    # ------------------------------------------------------------------ #
    #  BUSINESS RULES (все проверки до BEGIN IMMEDIATE)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _validate_business_rules(
        session: Session,
        *,
        now: datetime,
        staff_id: int,
        start_at: datetime,
        end_at: datetime,
    ) -> None:
        """
        Все бизнес-проверки, не требующие блокировки БД.
        Вызывается ДО BEGIN IMMEDIATE.

        Порядок проверок (от дешёвых к дорогим):
        1. Не в прошлом
        2. Lead time (минимум MIN_LEAD_TIME_MINUTES до start_at)
        3. Горизонт (не дальше BOOKING_HORIZON_DAYS)
        4. Slot alignment (start_at кратен SLOT_STEP_MINUTES)
        5. Рабочие часы + перерывы
        6. Time off
        """
        # 1. Нельзя бронировать в прошлом
        if start_at <= now:
            raise SlotUnavailableError("Нельзя бронировать в прошлом")

        # 2. Lead time
        earliest_allowed = now + timedelta(minutes=MIN_LEAD_TIME_MINUTES)
        if start_at < earliest_allowed:
            raise SlotUnavailableError(
                f"Бронирование возможно минимум за {MIN_LEAD_TIME_MINUTES} мин. "
                f"Ближайшее допустимое время: {earliest_allowed.isoformat()}"
            )

        # 3. Горизонт
        horizon_limit = now + timedelta(days=BOOKING_HORIZON_DAYS)
        if start_at > horizon_limit:
            raise SlotUnavailableError(
                f"Бронирование возможно не дальше {BOOKING_HORIZON_DAYS} дней вперёд"
            )

        # 4. Slot alignment
        if start_at.minute % SLOT_STEP_MINUTES != 0 or start_at.second != 0:
            raise SlotUnavailableError(
                f"start_at должен быть кратен {SLOT_STEP_MINUTES} минутам "
                f"(например, 10:00, 10:15, 10:30, 10:45)"
            )

        # 5. Рабочие часы + перерывы
        BookingService._validate_working_hours(
            session,
            staff_id=staff_id,
            start_at=start_at,
            end_at=end_at,
        )

        # 6. Time off
        BookingService._validate_no_time_off(
            session,
            staff_id=staff_id,
            start_at=start_at,
            end_at=end_at,
        )

    # ------------------------------------------------------------------ #
    #  PRIVATE HELPERS
    # ------------------------------------------------------------------ #

    @staticmethod
    def _resolve_staff_service(
        session: Session,
        *,
        business_id: int,
        staff_id: int,
        service_id: int,
    ) -> StaffService:
        """
        Находит активную связку staff ↔ service.
        Проверяет, что staff и service принадлежат указанному business_id.
        """
        # Проверка принадлежности staff к бизнесу
        staff = session.get(Staff, staff_id)
        if staff is None or staff.business_id != business_id:
            raise BookingNotFoundError(
                f"Сотрудник staff_id={staff_id} не найден в бизнесе {business_id}"
            )

        # Проверка принадлежности service к бизнесу
        service = session.get(Service, service_id)
        if service is None or service.business_id != business_id:
            raise BookingNotFoundError(
                f"Услуга service_id={service_id} не найдена в бизнесе {business_id}"
            )

        staff_services = staff_services_repo.get_for_staff(
            session, staff_id=staff_id,
        )
        for ss in staff_services:
            if ss.service_id == service_id and ss.is_active:
                if ss.duration <= 0:
                    raise BookingError("StaffService.duration должен быть > 0")
                return ss

        raise BookingNotFoundError(
            f"Активная связка staff_id={staff_id}, service_id={service_id} не найдена"
        )

    @staticmethod
    def _validate_working_hours(
        session: Session,
        *,
        staff_id: int,
        start_at: datetime,
        end_at: datetime,
    ) -> None:
        """
        Проверяет, что [start_at, end_at) полностью попадает
        в рабочие часы сотрудника и не пересекает перерыв.
        """
        weekday = start_at.weekday()
        wh_list = working_hours_repo.get_for_staff_and_weekday(
            session, staff_id=staff_id, weekday=weekday,
        )

        if not wh_list:
            raise SlotUnavailableError(
                f"У сотрудника нет рабочих часов на {start_at.strftime('%A')}"
            )

        booking_start_time = start_at.time()
        booking_end_time = end_at.time()

        fits_any = False
        for wh in wh_list:
            # Слот должен полностью попадать в рабочий диапазон
            if booking_start_time < wh.start_time:
                continue
            if booking_end_time > wh.end_time:
                continue

            # Проверка перерыва: если слот пересекает перерыв,
            # этот wh не подходит — пробуем следующий
            if wh.break_start and wh.break_end:
                if booking_start_time < wh.break_end and booking_end_time > wh.break_start:
                    continue

            fits_any = True
            break

        if not fits_any:
            raise SlotUnavailableError(
                "Слот не попадает в рабочие часы сотрудника "
                "или пересекает перерыв"
            )

    @staticmethod
    def _validate_no_time_off(
        session: Session,
        *,
        staff_id: int,
        start_at: datetime,
        end_at: datetime,
    ) -> None:
        """Проверяет, что слот не пересекает ни один TimeOff."""
        time_offs = time_off_repo.get_for_staff_and_period(
            session, staff_id=staff_id, start=start_at, end=end_at,
        )
        if time_offs:
            raise SlotUnavailableError(
                "Слот пересекает отгул/выходной сотрудника"
            )

    @staticmethod
    def _begin_immediate(session: Session) -> None:
        """
        SQLite: BEGIN IMMEDIATE захватывает RESERVED lock на БД,
        предотвращая конкурентные записи до COMMIT/ROLLBACK.

        Как это работает:
        1. Закрываем текущую неявную (DEFERRED) транзакцию SQLAlchemy
           через rollback — все предыдущие чтения уже завершены,
           нужные данные сохранены в Python-переменных.
        2. Начинаем новую транзакцию с BEGIN IMMEDIATE на уровне DBAPI,
           что захватывает RESERVED lock немедленно.

        При переходе на PostgreSQL этот метод заменяется на
        SELECT ... FOR UPDATE или SERIALIZABLE isolation level.
        """
        # Завершаем неявную read-транзакцию SQLAlchemy
        session.rollback()
        # Получаем сырое DBAPI-соединение и начинаем IMMEDIATE
        raw_conn = session.connection().connection.dbapi_connection
        raw_conn.isolation_level = None  # выключаем autocommit pysqlite
        raw_conn.execute("BEGIN IMMEDIATE")
