from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

class PostLike(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id")
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship 설정
    post: Optional["Post"] = Relationship(back_populates="likes")
    user: Optional["User"] = Relationship(back_populates="post_likes")

class CommentLike(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    comment_id: int = Field(foreign_key="comment.id")
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship 설정
    comment: Optional["Comment"] = Relationship(back_populates="likes")
    user: Optional["User"] = Relationship(back_populates="comment_likes")
