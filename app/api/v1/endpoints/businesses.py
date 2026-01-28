from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.business import BusinessCreate, BusinessRead
from app.services.business_service import create_business, get_businesses

router = APIRouter()


@router.post("/", response_model=BusinessRead)
def create(data: BusinessCreate, db: Session = Depends(get_db)):
    return create_business(db, data)


@router.get("/", response_model=list[BusinessRead])
def list_all(db: Session = Depends(get_db)):
    return get_businesses(db)
