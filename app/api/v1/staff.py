from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.staff import StaffCreate, StaffUpdate, StaffRead
from app.services.staff import StaffService

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
