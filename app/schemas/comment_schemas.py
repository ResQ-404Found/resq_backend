# schemas/comment_schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class CommentCreate(BaseModel):
    post_id: int
    content: str
    parent_comment_id: Optional[int] = None

class CommentUpdate(BaseModel):
    content: str

class Author(BaseModel):
    username: str
    profile_imageURL: Optional[str] = None

class CommentRead(BaseModel):
    id: int
    post_id: int
    user_id: int
    parent_comment_id: Optional[int]
    content: str
    created_at: datetime
    last_modified: Optional[datetime]
    like_count: int
    is_deleted: bool
    author: Author
    replies: List["CommentRead"] = []



