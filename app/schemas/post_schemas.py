from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class PostCreate(BaseModel):
    title: str
    content: str
    region_id: int
    post_imageURLs: List[str] = []

class PostRead(PostCreate):
    id: int
    user_id: int
    created_at: datetime
    view_count: int
    like_count: int

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