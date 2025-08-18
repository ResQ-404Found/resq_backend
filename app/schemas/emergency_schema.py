from typing import Optional, List
from pydantic import BaseModel, Field

# ------- Emergency Contact -------
class EmergencyContactCreate(BaseModel):
    target_user_id: int
    relation: Optional[str] = None
    is_emergency: bool = False

class EmergencyContactRead(BaseModel):
    id: int
    target_user_id: int
    relation: Optional[str] = None
    is_emergency: bool
    target_username: Optional[str] = None
    target_profile_imageURL: Optional[str] = None
    class Config:
        orm_mode = True

class EmergencyContactUpdate(BaseModel):
    relation: Optional[str] = None

# ------- Emergency Broadcast -------
class EmergencyBroadcastCreate(BaseModel):
    message: str = Field(example="긴급 상황입니다. 연락 부탁합니다.")
    include_location: bool = True
    contact_ids: Optional[List[int]] = None  # 없으면 is_emergency=True 대상 전체
    lat: Optional[float] = None
    lon: Optional[float] = None
    address: Optional[str] = None

class EmergencyBroadcastRead(BaseModel):
    id: int
    class Config:
        orm_mode = True
