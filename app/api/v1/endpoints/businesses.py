from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.business import BusinessCreate, BusinessRead
from app.models.business import Business
from app.models.business_user import BusinessUser, BusinessRole
from app.models.user import User


router = APIRouter()


@router.post("/", response_model=BusinessRead, status_code=status.HTTP_201_CREATED)
def create_business(
    data: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business = Business(
        name=data.name,
        timezone=data.timezone,
    )
    db.add(business)
    db.flush()

    bu = BusinessUser(
        user_id=current_user.id,
        business_id=business.id,
        role=BusinessRole.OWNER,
    )
    db.add(bu)
    db.commit()
    db.refresh(business)
    return business


@router.get("/", response_model=list[BusinessRead])
def list_my_businesses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bus = (
        db.query(Business)
        .join(BusinessUser, BusinessUser.business_id == Business.id)
        .filter(BusinessUser.user_id == current_user.id)
        .all()
    )
    return bus
