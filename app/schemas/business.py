from pydantic import BaseModel


class BusinessBase(BaseModel):
    name: str
    timezone: str = "UTC"


class BusinessCreate(BusinessBase):
    pass


class BusinessRead(BusinessBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
