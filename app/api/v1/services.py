from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.services import ServiceCreate, ServiceUpdate, ServiceRead
from app.services.services import ServiceService
from app.schemas.staff import StaffRead

router = APIRouter()


@router.post(
    "/",
    response_model=ServiceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_service(
    data: ServiceCreate,
    db: Session = Depends(get_db),
):
    return ServiceService.create_service(db, data)


@router.get(
    "/",
    response_model=list[ServiceRead],
)
def list_services(
    only_active: bool = True,
    db: Session = Depends(get_db),
):
    return ServiceService.list_services(db, only_active)


@router.get(
    "/{service_id}",
    response_model=ServiceRead,
)
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
):
    return ServiceService.get_service(db, service_id)


@router.patch(
    "/{service_id}",
    response_model=ServiceRead,
)
def update_service(
    service_id: int,
    data: ServiceUpdate,
    db: Session = Depends(get_db),
):
    return ServiceService.update_service(db, service_id, data)


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
):
    ServiceService.delete_service(db, service_id)

@router.get(
    "/{service_id}/staff",
    response_model=list[StaffRead],
)
def list_staff_for_service(
    service_id: int,
    db: Session = Depends(get_db),
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return service.staff

