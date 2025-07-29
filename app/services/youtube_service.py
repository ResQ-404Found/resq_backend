import os
from typing import List
from googleapiclient.discovery import build
from app.schemas.youtube_schema import YouTubeVideo
from typing import Optional

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

class YouTubeService:
    def __init__(self):
        self.service = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    def search_videos(self, query: str, max_results: int = 5) -> List[YouTubeVideo]:
        req = self.service.search().list(
            part="snippet",
            q=query,
            type="video",
            order="date",
            maxResults=max_results
        )
        res = req.execute()

        videos: List[YouTubeVideo] = []
        for item in res.get("items", []):
            vid = item["id"]["videoId"]
            snip = item["snippet"]
            videos.append(YouTubeVideo(
                title=snip["title"],
                video_url=f"https://www.youtube.com/watch?v={vid}",
                channel_title=snip["channelTitle"],
                published_at=snip["publishedAt"],
                thumbnail_url=snip["thumbnails"]["high"]["url"]
            ))
        return videos

    def search_combined(self, query: Optional[str], channel_name: Optional[str], max_results: int = 5) -> List[YouTubeVideo]:
        channel_id = None

        # 1. 채널 이름이 있는 경우 → channelId 찾기
        if channel_name:
            channel_search = self.service.search().list(
                part="snippet",
                q=channel_name,
                type="channel",
                maxResults=1
            ).execute()

            if not channel_search["items"]:
                raise ValueError("해당 채널을 찾을 수 없습니다.")

            channel_id = channel_search["items"][0]["id"]["channelId"]

        # 2. 영상 검색 조건 구성
        video_params = {
            "part": "snippet",
            "type": "video",
            "order": "date",        # 최신순 ✅
            "maxResults": max_results
        }

        if query:
            video_params["q"] = query
        if channel_id:
            video_params["channelId"] = channel_id

        # 3. 요청 실행
        video_search = self.service.search().list(**video_params).execute()

        videos = []
        for item in video_search.get("items", []):
            vid = item["id"]["videoId"]
            snip = item["snippet"]
            videos.append(YouTubeVideo(
                title=snip["title"],
                video_url=f"https://www.youtube.com/watch?v={vid}",
                channel_title=snip["channelTitle"],
                published_at=snip["publishedAt"],
                thumbnail_url=snip["thumbnails"]["high"]["url"]
            ))

        return videos
