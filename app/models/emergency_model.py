# app/models/emergency_model.py
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, UniqueConstraint

class EmergencyContact(SQLModel, table=True):
    __tablename__ = "emergency_contact"
    __table_args__ = (UniqueConstraint("user_id", "target_user_id",
                                       name="uq_emergency_contact_owner_target"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)        # 소유자(나)
    target_user_id: int = Field(foreign_key="user.id", index=True) # 대상(친구)
    relation: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EmergencyLocation(SQLModel, table=True):
    __tablename__ = "emergency_location"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    lat: float
    lon: float
    address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EmergencyBroadcast(SQLModel, table=True):
    __tablename__ = "emergency_broadcast"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    message: str
    include_location: bool = True
    location_id: Optional[int] = Field(foreign_key="emergency_location.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EmergencyBroadcastRecipient(SQLModel, table=True):
    __tablename__ = "emergency_broadcast_recipient"
    id: Optional[int] = Field(default=None, primary_key=True)
    broadcast_id: int = Field(foreign_key="emergency_broadcast.id", index=True)
    contact_id: int = Field(foreign_key="emergency_contact.id", index=True)
    channel: str = "push"                # push만 사용
    status: str = "queued"               # queued/sent/failed
    provider_message_id: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
