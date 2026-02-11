# app/api/v1/endpoints/bookings.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_business, BusinessContext
from app.schemas.booking import BookingCreate, BookingRead, BookingCancel
from app.models.booking import Booking
from app.services.booking_service import (
    BookingService,
    BookingNotFoundError,
    BookingStateError,
    SlotUnavailableError,
)

router = APIRouter(tags=["Bookings"])

_booking_service = BookingService()


@router.get(
    "/bookings",
    response_model=list[BookingRead],
    summary="Список бронирований бизнеса",
)
def list_bookings(
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    return (
        db.query(Booking)
        .filter(
            Booking.business_id == ctx.business_id,
            Booking.is_active == True,
        )
        .order_by(Booking.start_at.desc())
        .all()
    )


@router.post(
    "/bookings",
    response_model=BookingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать бронирование",
)
def create_booking(
    body: BookingCreate,
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    try:
        booking = _booking_service.create_booking(
            db,
            business_id=ctx.business_id,
            staff_id=body.staff_id,
            service_id=body.service_id,
            start_at=body.start_at,
            confirm=body.confirm,
            customer_name=body.customer.name,
            customer_phone=body.customer.phone,
            customer_email=body.customer.email,
            comment=body.comment,
        )
    except SlotUnavailableError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except BookingNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return booking


@router.post(
    "/bookings/{booking_id}/confirm",
    response_model=BookingRead,
    summary="Подтвердить HOLD-бронирование",
)
def confirm_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    try:
        booking = _booking_service.confirm_booking(
            db, booking_id, business_id=ctx.business_id,
        )
    except BookingNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BookingStateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return booking


@router.post(
    "/bookings/{booking_id}/cancel",
    response_model=BookingRead,
    summary="Отменить бронирование",
)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    try:
        booking = _booking_service.cancel_booking(
            db, booking_id, business_id=ctx.business_id,
        )
    except BookingNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BookingStateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return booking
