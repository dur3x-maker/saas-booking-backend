from datetime import time
from pydantic import BaseModel, Field


class WorkingHoursBase(BaseModel):
    staff_id: int
    weekday: int = Field(ge=0, le=6, description="0 = Monday, 6 = Sunday")
    start_time: time
    end_time: time
    break_start: time | None = None
    break_end: time | None = None
    is_active: bool = True


class WorkingHoursCreate(WorkingHoursBase):
    pass


class WorkingHoursRead(WorkingHoursBase):
    id: int

    class Config:
        from_attributes = True
