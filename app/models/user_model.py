from sqlmodel import SQLModel, Field
from typing import Optional
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
    login_id: str = Field(nullable=False, unique=True)
    email: str = Field(nullable=False, unique=True)
    password: str = Field(nullable=False)
    username: str = Field(nullable=False, unique=True)
    profile_imageURL: Optional[str] = Field(default=None)
    role: UserRole = Field(default=UserRole.USER)
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)