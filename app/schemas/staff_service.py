from pydantic import BaseModel


class StaffServiceRead(BaseModel):
    service_id: int
    service_name: str
    price: int
    duration: int | None
    is_active: bool

    class Config:
        from_attributes = True
