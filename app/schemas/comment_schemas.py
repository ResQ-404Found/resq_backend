# schemas/comment_schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommentCreate(BaseModel):
    post_id: int
    content: str

class CommentUpdate(BaseModel):
    content: str

class CommentRead(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: datetime
    last_modified: Optional[datetime]
    like_count: int

