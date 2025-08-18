from datetime import datetime
from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field, UniqueConstraint

class FriendStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"

class FriendRequest(SQLModel, table=True):
    __tablename__ = "friend_request"
    __table_args__ = (UniqueConstraint("requester_id", "addressee_id", name="uq_friend_request_pair"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    requester_id: int = Field(foreign_key="user.id", index=True)
    addressee_id: int = Field(foreign_key="user.id", index=True)
    status: FriendStatus = Field(default=FriendStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None

class FriendFavorite(SQLModel, table=True):
    __tablename__ = "friend_favorite"
    __table_args__ = (UniqueConstraint("user_id", "friend_user_id", name="uq_friend_favorite_owner_friend"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    friend_user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)