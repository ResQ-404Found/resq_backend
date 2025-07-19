from typing import Optional, List
from pydantic import BaseModel


class HospitalOperatingHourRead(BaseModel):
    day_of_week: str
    open_time: Optional[str]
    close_time: Optional[str]
    is_closed: bool

    class Config:
        orm_mode = True


class HospitalRead(BaseModel):
    id: int
    facility_name: str
    road_address: str
    latitude: float
    longitude: float
    phone_number: Optional[str]
    operating_hours: List[HospitalOperatingHourRead]

    class Config:
        orm_mode = True
