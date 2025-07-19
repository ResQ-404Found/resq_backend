from fastapi import APIRouter, HTTPException, Query
from app.services.youtube_service import YouTubeService
from app.schemas.youtube_schema import YouTubeVideo

router = APIRouter()

@router.get("/youtube", response_model=list[YouTubeVideo])
def search_youtube(query: str = Query(..., description="검색어는 필수입니다")):
    try:
        service = YouTubeService()
        return service.search_videos(query=query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"YouTube 검색 실패: {e}")
