from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship, JSON
from sqlalchemy import Column,String
from sqlalchemy.dialects.postgresql import JSON

class Post(SQLModel,table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    type: str
    title:str
    content:str = Field(sa_column=Column(String(500)))
    region_id: Optional[int] = Field(default=None, foreign_key="region.id", nullable=True)
    post_imageURLs: List[str] = Field(
    sa_column=Column(JSON, default=[])
)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    view_count : int = Field(default=0)
    like_count : int = Field(default=0)
    user: Optional["User"] = Relationship(back_populates="posts")
    region: Optional["Region"] = Relationship(back_populates="posts")
    likes: List["PostLike"] = Relationship(
        back_populates="post", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    comments: List["Comment"] = Relationship(
        back_populates="post",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

