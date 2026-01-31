from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.staff import StaffRepository
from app.schemas.staff import StaffCreate, StaffUpdate


class StaffService:

    @staticmethod
    def create_staff(db: Session, data: StaffCreate):
        return StaffRepository.create(db, data)

    @staticmethod
    def get_staff(db: Session, staff_id: int):
        staff = StaffRepository.get_by_id(db, staff_id)
        if not staff:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff member not found"
            )
        return staff

    @staticmethod
    def list_staff(db: Session, only_active: bool = True):
        return StaffRepository.list(db, only_active)

    @staticmethod
    def update_staff(
        db: Session,
        staff_id: int,
        data: StaffUpdate
    ):
        staff = StaffService.get_staff(db, staff_id)
        return StaffRepository.update(db, staff, data)

    @staticmethod
    def delete_staff(db: Session, staff_id: int):
        staff = StaffService.get_staff(db, staff_id)
        return StaffRepository.soft_delete(db, staff)
