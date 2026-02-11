from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_business, BusinessContext
from app.schemas.staff import StaffCreate, StaffUpdate, StaffRead
from app.services.staff import StaffService
from app.models.staff_service import StaffService as StaffServiceModel
from app.schemas.staff_service import StaffServiceRead
from app.models.service import Service
from app.schemas.services import ServiceRead
from app.models.staff import Staff


router = APIRouter(tags=["Staff"])


@router.post(
    "/staff",
    response_model=StaffRead,
    status_code=status.HTTP_201_CREATED,
)
def create_staff(
    data: StaffCreate,
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    return StaffService.create_staff(db, data, business_id=ctx.business_id)


@router.get(
    "/staff",
    response_model=list[StaffRead],
)
def list_staff(
    only_active: bool = True,
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    return StaffService.list_staff(db, only_active, business_id=ctx.business_id)


@router.get(
    "/staff/{staff_id}",
    response_model=StaffRead,
)
def get_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    return StaffService.get_staff(db, staff_id, business_id=ctx.business_id)


@router.patch(
    "/staff/{staff_id}",
    response_model=StaffRead,
)
def update_staff(
    staff_id: int,
    data: StaffUpdate,
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    return StaffService.update_staff(db, staff_id, data, business_id=ctx.business_id)


@router.delete(
    "/staff/{staff_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    StaffService.delete_staff(db, staff_id, business_id=ctx.business_id)


@router.post(
    "/staff/{staff_id}/services/{service_id}",
    status_code=status.HTTP_201_CREATED,
)
def attach_service_to_staff(
    staff_id: int,
    service_id: int,
    price: int,
    duration: int | None = None,
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    business_id = ctx.business_id
    staff = db.query(Staff).filter(
        Staff.id == staff_id, Staff.business_id == business_id,
    ).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    service = db.query(Service).filter(
        Service.id == service_id, Service.business_id == business_id,
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    existing = (
        db.query(StaffServiceModel)
        .filter(
            StaffServiceModel.staff_id == staff_id,
            StaffServiceModel.service_id == service_id,
            StaffServiceModel.is_active == True,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Service already attached to staff",
        )

    staff_service = StaffServiceModel(
        staff_id=staff_id,
        service_id=service_id,
        price=price,
        duration=duration,
    )

    db.add(staff_service)
    db.commit()

    return {"detail": "Service attached to staff"}



@router.delete(
    "/staff/{staff_id}/services/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def detach_service_from_staff(
    staff_id: int,
    service_id: int,
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    staff_service = (
        db.query(StaffServiceModel)
        .filter(
            StaffServiceModel.staff_id == staff_id,
            StaffServiceModel.service_id == service_id,
            StaffServiceModel.is_active == True,
        )
        .first()
    )

    if not staff_service:
        raise HTTPException(
            status_code=404,
            detail="Service not attached to staff",
        )

    staff_service.is_active = False
    db.commit()


@router.get(
    "/staff/{staff_id}/services",
    response_model=list[StaffServiceRead],
)
def list_services_for_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    staff = db.query(Staff).filter(
        Staff.id == staff_id, Staff.business_id == ctx.business_id,
    ).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    return [
        StaffServiceRead(
            service_id=ss.service.id,
            service_name=ss.service.name,
            price=ss.price,
            duration=ss.duration,
            is_active=ss.is_active,
        )
        for ss in staff.staff_services
        if ss.is_active
    ]


