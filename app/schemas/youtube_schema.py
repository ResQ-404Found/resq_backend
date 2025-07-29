from pydantic import BaseModel

class YouTubeVideo(BaseModel):
    title: str
    video_url: str
    channel_title: str
    published_at: str
    thumbnail_url: str
