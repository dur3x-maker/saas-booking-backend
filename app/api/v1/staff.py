from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.staff import StaffCreate, StaffUpdate, StaffRead
from app.services.staff import StaffService
from app.models.service import Service
from app.schemas.services import ServiceRead


router = APIRouter()


@router.post(
    "/",
    response_model=StaffRead,
    status_code=status.HTTP_201_CREATED,
)
def create_staff(
    data: StaffCreate,
    db: Session = Depends(get_db),
):
    return StaffService.create_staff(db, data)


@router.get(
    "/",
    response_model=list[StaffRead],
)
def list_staff(
    only_active: bool = True,
    db: Session = Depends(get_db),
):
    return StaffService.list_staff(db, only_active)


@router.get(
    "/{staff_id}",
    response_model=StaffRead,
)
def get_staff(
    staff_id: int,
    db: Session = Depends(get_db),
):
    return StaffService.get_staff(db, staff_id)


@router.patch(
    "/{staff_id}",
    response_model=StaffRead,
)
def update_staff(
    staff_id: int,
    data: StaffUpdate,
    db: Session = Depends(get_db),
):
    return StaffService.update_staff(db, staff_id, data)


@router.delete(
    "/{staff_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_staff(
    staff_id: int,
    db: Session = Depends(get_db),
):
    StaffService.delete_staff(db, staff_id)


@router.post(
    "/{staff_id}/services/{service_id}",
    status_code=status.HTTP_201_CREATED,
)
def attach_service_to_staff(
    staff_id: int,
    service_id: int,
    db: Session = Depends(get_db),
):
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if service in staff.services:
        raise HTTPException(
            status_code=400,
            detail="Service already attached to staff",
        )

    staff.services.append(service)
    db.commit()

    return {"detail": "Service attached to staff"}


@router.delete(
    "/{staff_id}/services/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def detach_service_from_staff(
    staff_id: int,
    service_id: int,
    db: Session = Depends(get_db),
):
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if service not in staff.services:
        raise HTTPException(
            status_code=400,
            detail="Service not attached to staff",
        )

    staff.services.remove(service)
    db.commit()

@router.get(
    "/{staff_id}/services",
    response_model=list[ServiceRead],
)
def list_services_for_staff(
    staff_id: int,
    db: Session = Depends(get_db),
):
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    return staff.services

