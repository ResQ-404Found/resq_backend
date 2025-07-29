from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# 목록용
class NewsRead(BaseModel):
    id: int
    title: str
    pub_date: datetime
    description: str
    naver_url: str
    origin_url: Optional[str] = None

    class Config:
        orm_mode = True

# 요약 응답
class NewsSummaryResponse(BaseModel):
    summary: str
