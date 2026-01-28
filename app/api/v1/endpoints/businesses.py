from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.business import BusinessCreate, BusinessRead
from app.services.business_service import create_business, get_businesses
from app.api.deps import get_current_user
from app.models.user import User


router = APIRouter()


@router.post("/", response_model=BusinessRead)
def create(
    data: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_business(db, data, owner=current_user)



@router.get("/", response_model=list[BusinessRead])
def list_all(db: Session = Depends(get_db)):
    return get_businesses(db)
