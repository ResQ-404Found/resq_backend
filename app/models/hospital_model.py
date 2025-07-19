from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class Hospital(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    facility_name: str                      # INST_NM
    road_address: str                       # ADDR
    latitude: float                         # HSPTL_LAT
    longitude: float                        # HSPTL_LOT
    phone_number: Optional[str] = None      # TELNO
    emergency_room: Optional[bool] = None   # EMR_OPERT_YN == 'Y'
    weekend_operating: Optional[bool] = None # WKND_OPERT_YN == 'Y'


class HospitalOperatingHour(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hospital_id: int = Field(foreign_key="hospital.id")
    day_of_week: str
    open_time: Optional[str]
    close_time: Optional[str]
    is_closed: bool
