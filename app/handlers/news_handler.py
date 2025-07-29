from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.db.session import get_db_session
from app.services.news_service import NewsService
from app.schemas.news_schemas import (
    NewsRead,
    NewsSummaryResponse
)

router = APIRouter()

# 뉴스 검색 및 저장
@router.get("/news/", response_model=list[NewsRead])
def list_news(query: str = Query(..., description="검색어는 필수입니다"), session: Session = Depends(get_db_session)):
    service = NewsService(session)
    try:
        news_list = service.fetch_news_from_naver(query=query)
        return news_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 검색 실패: {e}")


@router.post("/news/ai", response_model=NewsSummaryResponse)
def generate_summary(session: Session = Depends(get_db_session)):
    service = NewsService(session)
    try:
        summary = service.generate_hot_keywords_summary(limit=3)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"키워드 요약 실패: {e}")
