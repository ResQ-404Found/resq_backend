from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class NotificationCreate(BaseModel):
    disaster_id: int
    title: str
    body: str

class NotificationRead(BaseModel):
    id: int
    user_id: int
    disaster_id: int
    created_at: datetime
    title: str
    body: str
    is_sent: bool
    send_at: Optional[datetime]

