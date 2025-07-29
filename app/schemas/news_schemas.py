from datetime import datetime
from pydantic import BaseModel

# 목록용
class NewsRead(BaseModel):
    id: int
    title: str
    pub_date: datetime

    class Config:
        orm_mode = True

# 상세용 (본문 포함)
class NewsDetail(BaseModel):
    id: int
    title: str
    origin_url: str
    naver_url: str
    pub_date: datetime
    full_text: str

    class Config:
        orm_mode = True

# 요약 요청
class NewsSummaryRequest(BaseModel):
    news_id: int

# 요약 응답
class NewsSummaryResponse(BaseModel):
    summary: str
