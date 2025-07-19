from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class PostCreate(BaseModel):
    title: str
    content: str
    region_id: int
    post_imageURLs: List[str] = []

class Author(BaseModel):
    id: int
    username: str
    profile_imageURL: Optional[str] = None

class PostRead(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    region_id: int
    post_imageURLs: List[str] = []
    created_at: datetime
    view_count: int
    like_count: int
    author: Author

    model_config = {
        "from_attributes": True
    }

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    region_id: Optional[int] = None
    post_imageURLs: Optional[List[str]] = None

    model_config = {
        "from_attributes": True
    }