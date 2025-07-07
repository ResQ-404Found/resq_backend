from typing import Optional
from pydantic import BaseModel

class NotificationRegionCreate(BaseModel):
    region_id: int

class NotificationRegionRead(BaseModel):
    id: int
    user_id: int
    region_id: int
