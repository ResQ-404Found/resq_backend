from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

class FriendRequestCreate(BaseModel):
    username: str = Field(..., description="상대 닉네임(=username)")

class FriendRequestRead(BaseModel):
    id: int
    requester_id: int
    addressee_id: int
    status: str
    requester_username: str | None = None
    addressee_username: str | None = None
    class Config: orm_mode = True
