from pydantic import BaseModel


class BusinessBase(BaseModel):
    name: str
    timezone: str = "UTC"


class BusinessCreate(BusinessBase):
    pass


class BusinessRead(BusinessBase):
    id: int
    is_active: bool
    owner_id: int | None

    class Config:
        from_attributes = True
