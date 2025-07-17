from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    login_id: str = Field(nullable=False)
    email: str = Field(nullable=False)
    password: str = Field(nullable=False)
    username: str = Field(nullable=False)
    point: int = 0
    profile_imageURL: Optional[str] = Field(default=None)
    role: UserRole = Field(default=UserRole.USER)
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    fcm_token: Optional[str] = Field(default=None, nullable=True)
    
    # 좋아요 relationship
    post_likes: List["PostLike"] = Relationship(back_populates="user")
    comment_likes: List["CommentLike"] = Relationship(back_populates="user")
    notification_disastertypes: List["NotificationDisasterType"] = Relationship(back_populates="user")
    notification_regions: List["NotificationRegion"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")