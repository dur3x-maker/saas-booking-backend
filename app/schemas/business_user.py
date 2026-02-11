from pydantic import BaseModel, EmailStr

from app.models.business_user import BusinessRole


class BusinessUserRead(BaseModel):
    user_id: int
    business_id: int
    role: BusinessRole
    email: str | None = None

    model_config = {"from_attributes": True}


class BusinessUserInvite(BaseModel):
    email: EmailStr
    role: BusinessRole = BusinessRole.ADMIN


class BusinessUserUpdate(BaseModel):
    role: BusinessRole
