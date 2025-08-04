from fastapi import APIRouter, HTTPException, Query
from app.services.youtube_service import YouTubeService
from app.schemas.youtube_schema import YouTubeVideo
from typing import Optional,List

router = APIRouter()

@router.get("/youtube", response_model=List[YouTubeVideo])
def search_youtube(
    query: Optional[str] = Query(None, description="검색어"),
    channel: Optional[str] = Query(None, description="채널명"),
    limit: int = Query(5, ge=1, le=20, description="최대 반환 개수")
):
    service = YouTubeService()
    try:
        videos = service.search_combined(query=query, channel_name=channel, max_results=limit)
        return videos  # 이미 최신순 정렬된 상태로 옴
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"YouTube 검색 실패: {e}")
