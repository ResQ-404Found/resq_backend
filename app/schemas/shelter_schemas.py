from pydantic import BaseModel
from typing import Optional

class ShelterResponse(BaseModel):
    id: int
    facility_name: str
    road_address: Optional[str]
    latitude: float
    longitude: float
    shelter_type_code: Optional[int]
    shelter_type_name: Optional[str]
    management_serial_number: Optional[str]

    class Config:
        from_attributes = True
