# models/comment_model.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id")
    user_id: int = Field(foreign_key="user.id")
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_modified: Optional[datetime] = None
    like_count: int = 0
    
    likes: List["CommentLike"] = Relationship(back_populates="comment")