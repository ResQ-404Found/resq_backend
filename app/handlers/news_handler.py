from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.db.session import get_db_session
from app.services.news_service import NewsService
from app.schemas.news_schemas import (
    NewsRead,
    NewsDetail,
    NewsSummaryRequest,
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

# 뉴스 상세 조회 (본문 크롤링 or fallback)
@router.get("/news/{news_id}", response_model=NewsDetail)
def read_news_detail(news_id: int, session: Session = Depends(get_db_session)):
    service = NewsService(session)
    try:
        news = service.get_news_by_id(news_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="뉴스를 찾을 수 없습니다.")

    full_text = service.fetch_full_text(news.naver_url)

    # 크롤링 실패 시 → description 대체
    if full_text == "본문을 가져올 수 없습니다.":
        fallback = service.fetch_description_from_api(news.title)
        if fallback:
            full_text = f"{fallback.strip()}\n\n[자세한 기사 보기] {news.naver_url}"

    return {
        **news.dict(),
        "full_text": full_text
    }

# 버튼 클릭 시 요약 반환
@router.post("/news/ai", response_model=NewsSummaryResponse)
def generate_summary(req: NewsSummaryRequest, session: Session = Depends(get_db_session)):
    service = NewsService(session)
    try:
        summary = service.generate_summary_by_news_id(req.news_id)
        return {"summary": summary}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"요약 실패: {e}")
