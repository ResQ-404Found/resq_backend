import os
from typing import List
from googleapiclient.discovery import build
from app.schemas.youtube_schema import YouTubeVideo

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
