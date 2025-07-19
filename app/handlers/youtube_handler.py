from fastapi import APIRouter, HTTPException, Query
from app.services.youtube_service import YouTubeService
from app.schemas.youtube_schema import YouTubeVideo
from typing import Optional,List

router = APIRouter()

@router.get("/youtube", response_model=List[YouTubeVideo])
def search_youtube(
    query: Optional[str] = Query(None, description="검색어"),
    channel: Optional[str] = Query(None, description="채널명")
):
    service = YouTubeService()
    try:
        return service.search_combined(query=query, channel_name=channel)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"YouTube 검색 실패: {e}")
