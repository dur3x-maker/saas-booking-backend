# app/services/services.py

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.services import ServiceRepository
from app.schemas.services import ServiceCreate, ServiceUpdate


class ServiceService:

    @staticmethod
    def create_service(db: Session, data: ServiceCreate, *, business_id: int):
        return ServiceRepository.create(db, data, business_id=business_id)

    @staticmethod
    def get_service(db: Session, service_id: int, *, business_id: int):
        service = ServiceRepository.get_by_id(db, service_id, business_id=business_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        return service

    @staticmethod
    def list_services(db: Session, only_active: bool = True, *, business_id: int):
        return ServiceRepository.list(db, only_active, business_id=business_id)

    @staticmethod
    def update_service(
        db: Session,
        service_id: int,
        data: ServiceUpdate,
        *,
        business_id: int,
    ):
        service = ServiceService.get_service(db, service_id, business_id=business_id)
        return ServiceRepository.update(db, service, data)

    @staticmethod
    def delete_service(db: Session, service_id: int, *, business_id: int):
        service = ServiceService.get_service(db, service_id, business_id=business_id)
        return ServiceRepository.soft_delete(db, service)
