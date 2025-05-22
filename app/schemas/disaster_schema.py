from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class DisasterBase(BaseModel):
    disaster_type: str
    disaster_level: str
    info: str
    active: bool
    start_time: datetime
    updated_at: datetime
    region: str

class Disaster(DisasterBase):
    id: int

    class Config:
        from_attributes = True 
class DisasterSummaryResponse(BaseModel):
    message: str
    data: list

class DisasterDetailResponse(BaseModel):
    message: str
    data: Disaster