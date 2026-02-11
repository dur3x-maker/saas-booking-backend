# app/api/v1/endpoints/context.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_business, BusinessContext
from app.models.business import Business

router = APIRouter(tags=["Context"])


class ContextResponse(BaseModel):
    business_id: int
    business_name: str
    role: str


@router.get("/context", response_model=ContextResponse)
def get_context(
    db: Session = Depends(get_db),
    ctx: BusinessContext = Depends(get_current_business),
):
    biz = db.query(Business).filter(Business.id == ctx.business_id).first()
    return ContextResponse(
        business_id=ctx.business_id,
        business_name=biz.name if biz else "",
        role=ctx.role.value,
    )
