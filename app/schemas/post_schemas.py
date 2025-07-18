# app/schemas/post_schemas.py

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class Author(BaseModel):
    id: int
    nickname: str  # == username
    profile_image_url: Optional[str]  # == profile_imageURL

    model_config = {
        "from_attributes": True
    }


class PostCreate(BaseModel):
    title: str
    content: str
    region_id: int


class PostRead(BaseModel):
    id: int
    title: str
    content: str
    author: Author 
    created_at: datetime
    view_count: int
    like_count: int
    post_imageURLs: Optional[List[str]] = None
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
