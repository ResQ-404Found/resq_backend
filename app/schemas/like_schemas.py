from pydantic import BaseModel
from app.schemas.common_schema import ApiResponse

class LikeCount(BaseModel):
    like_count: int

class LikeStatus(BaseModel):
    liked: bool

LikeCountResponse = ApiResponse[LikeCount]
LikeStatusResponse = ApiResponse[LikeStatus]