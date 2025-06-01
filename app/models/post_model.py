from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship, JSON
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON

class Post(SQLModel,table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title:str
    content:str
    region_id: int = Field(foreign_key="region.id")
    post_imageURLs: List[str] = Field(
    sa_column=Column(JSON, default=[])
)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    view_count : int = Field(default=0)
    like_count : int = Field(default=0)
    
    region: Optional["Region"] = Relationship(back_populates="posts")
