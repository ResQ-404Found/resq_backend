from pydantic import BaseModel
from datetime import datetime

# 요청
class ChatRequest(BaseModel):
    message: str

# 응답
class ChatResponse(BaseModel):
    response: str

# 히스토리 조회용 응답
class ChatLogResponse(BaseModel):
    user_message: str
    bot_response: str
    created_at: datetime

    class Config:
        orm_mode = True
