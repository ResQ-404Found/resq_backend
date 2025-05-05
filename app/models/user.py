from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    login_id: str = Field(nullable=False, unique=True)
    email: str = Field(nullable=False, unique=True)
    password: str = Field(nullable=False)
    username: str = Field(nullable=False, unique=True)
    profile_imageURL: Optional[str] = None
    role: str = Field(default="user")
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)