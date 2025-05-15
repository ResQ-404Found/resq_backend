from sqlmodel import SQLModel, Field
from typing import Optional

class Shelter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    facility_name: str
    road_address: Optional[str]
    latitude: float
    longitude: float
    shelter_type_code: Optional[int]
    shelter_type_name: Optional[str]
    management_serial_number: Optional[str]
