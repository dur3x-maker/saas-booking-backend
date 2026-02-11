# app/api/v1/endpoints/me.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.business import Business
from app.models.business_user import BusinessUser

router = APIRouter(tags=["Me"])


class _UserInfo(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}


class _BusinessInfo(BaseModel):
    id: int
    name: str
    role: str


class MeResponse(BaseModel):
    user: _UserInfo
    businesses: list[_BusinessInfo]


@router.get("/me", response_model=MeResponse)
def get_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Business, BusinessUser.role)
        .join(BusinessUser, BusinessUser.business_id == Business.id)
        .filter(BusinessUser.user_id == current_user.id)
        .order_by(Business.id.asc())
        .all()
    )

    businesses = [
        _BusinessInfo(id=biz.id, name=biz.name, role=role.value)
        for biz, role in rows
    ]

    return MeResponse(
        user=_UserInfo(
            id=current_user.id,
            email=current_user.email,
            is_active=current_user.is_active,
            created_at=current_user.created_at.isoformat(),
        ),
        businesses=businesses,
    )
