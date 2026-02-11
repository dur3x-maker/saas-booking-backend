from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.services import ServiceCreate, ServiceUpdate, ServiceRead
from app.services.services import ServiceService
from app.schemas.staff import StaffRead

router = APIRouter(tags=["Services"])


@router.post(
    "/services",
    response_model=ServiceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_service(
    business_id: int,
    data: ServiceCreate,
    db: Session = Depends(get_db),
):
    return ServiceService.create_service(db, data, business_id=business_id)


@router.get(
    "/services",
    response_model=list[ServiceRead],
)
def list_services(
    business_id: int,
    only_active: bool = True,
    db: Session = Depends(get_db),
):
    return ServiceService.list_services(db, only_active, business_id=business_id)


@router.get(
    "/services/{service_id}",
    response_model=ServiceRead,
)
def get_service(
    business_id: int,
    service_id: int,
    db: Session = Depends(get_db),
):
    return ServiceService.get_service(db, service_id, business_id=business_id)


@router.patch(
    "/services/{service_id}",
    response_model=ServiceRead,
)
def update_service(
    business_id: int,
    service_id: int,
    data: ServiceUpdate,
    db: Session = Depends(get_db),
):
    return ServiceService.update_service(db, service_id, data, business_id=business_id)


@router.delete(
    "/services/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_service(
    business_id: int,
    service_id: int,
    db: Session = Depends(get_db),
):
    ServiceService.delete_service(db, service_id, business_id=business_id)

@router.get(
    "/services/{service_id}/staff",
    response_model=list[StaffRead],
)
def list_staff_for_service(
    business_id: int,
    service_id: int,
    db: Session = Depends(get_db),
):
    service = db.query(Service).filter(
        Service.id == service_id, Service.business_id == business_id,
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return service.staff

