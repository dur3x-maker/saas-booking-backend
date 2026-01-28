# app/repositories/services.py

from sqlalchemy.orm import Session

from app.models.service import Service
from app.schemas.services import ServiceCreate, ServiceUpdate


class ServiceRepository:

    @staticmethod
    def create(db: Session, data: ServiceCreate) -> Service:
        service = Service(**data.model_dump())
        db.add(service)
        db.commit()
        db.refresh(service)
        return service

    @staticmethod
    def get_by_id(db: Session, service_id: int) -> Service | None:
        return (
            db.query(Service)
            .filter(Service.id == service_id)
            .first()
        )

    @staticmethod
    def list(db: Session, only_active: bool = True) -> list[Service]:
        query = db.query(Service)
        if only_active:
            query = query.filter(Service.is_active.is_(True))
        return query.all()

    @staticmethod
    def update(
        db: Session,
        service: Service,
        data: ServiceUpdate
    ) -> Service:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(service, field, value)

        db.commit()
        db.refresh(service)
        return service

    @staticmethod
    def soft_delete(db: Session, service: Service) -> Service:
        service.is_active = False
        db.commit()
        db.refresh(service)
        return service
