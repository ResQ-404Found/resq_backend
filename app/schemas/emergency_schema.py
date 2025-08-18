# app/schemas/emergency_schema.py
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

# ---------- Contacts ----------
class EmergencyContactRead(BaseModel):
    id: int
    target_user_id: int
    relation: Optional[str] = None
    is_emergency: bool = True  # 행 존재 = TRUE (계산값)
    target_username: Optional[str] = None
    target_profile_imageURL: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# (안 쓰면 삭제 가능)
class EmergencyContactUpsert(BaseModel):
    relation: Optional[str] = Field(default=None, description="표시용 메모(가족/친구 등)")

# ---------- Broadcast: create / minimal read ----------
class EmergencyBroadcastCreate(BaseModel):
    message: str = Field(..., example="긴급 상황입니다. 연락 부탁합니다.")
    include_location: bool = True
    contact_ids: Optional[List[int]] = None  # 지정 없으면 등록된 비상연락 대상으로 전체 전송
    lat: Optional[float] = None
    lon: Optional[float] = None
    address: Optional[str] = None

class EmergencyBroadcastRead(BaseModel):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ---------- Broadcast: list/detail ----------
class EmergencyRecipientRead(BaseModel):
    id: int
    contact_id: int
    contact_target_user_id: Optional[int] = None
    contact_target_username: Optional[str] = None
    status: str                    # "sent" | "failed" | "queued"
    error: Optional[str] = None    # 실패 사유 (예: "missing_fcm_token")
    channel: str = "push"
    model_config = ConfigDict(from_attributes=True)

class EmergencyBroadcastSummaryRead(BaseModel):
    id: int
    message: str
    include_location: bool
    created_at: datetime
    total: int
    sent: int
    failed: int
    model_config = ConfigDict(from_attributes=True)

class EmergencyBroadcastDetailRead(BaseModel):
    id: int
    message: str
    include_location: bool
    created_at: datetime
    total: int
    sent: int
    failed: int
    recipients: List[EmergencyRecipientRead]
    model_config = ConfigDict(from_attributes=True)
