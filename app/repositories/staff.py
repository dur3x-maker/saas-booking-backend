from sqlalchemy.orm import Session

from app.models.staff import Staff
from app.schemas.staff import StaffCreate, StaffUpdate


class StaffRepository:

    @staticmethod
    def create(db: Session, data: StaffCreate, *, business_id: int) -> Staff:
        staff = Staff(**data.model_dump(), business_id=business_id)
        db.add(staff)
        db.commit()
        db.refresh(staff)
        return staff

    @staticmethod
    def get_by_id(
        db: Session, staff_id: int, *, business_id: int,
    ) -> Staff | None:
        return (
            db.query(Staff)
            .filter(
                Staff.id == staff_id,
                Staff.business_id == business_id,
            )
            .first()
        )

    @staticmethod
    def list(
        db: Session, only_active: bool = True, *, business_id: int,
    ) -> list[Staff]:
        query = db.query(Staff).filter(Staff.business_id == business_id)
        if only_active:
            query = query.filter(Staff.is_active.is_(True))
        return query.all()

    @staticmethod
    def update(
        db: Session,
        staff: Staff,
        data: StaffUpdate
    ) -> Staff:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(staff, field, value)

        db.commit()
        db.refresh(staff)
        return staff

    @staticmethod
    def soft_delete(db: Session, staff: Staff) -> Staff:
        staff.is_active = False
        db.commit()
        db.refresh(staff)
        return staff
