from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.chatbot_schema import ChatRequest, ChatResponse, ChatLogResponse
from app.services.chatbot_service import get_chat_response, save_chat_log, get_chat_logs
from app.models.user_model import User
from app.handlers.user_handler import get_current_user

router = APIRouter()
@router.post("/chatbot/chat", response_model=ChatResponse)
async def chat_with_bot(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        bot_reply = get_chat_response(request.message)
        save_chat_log(user_id=current_user.id, user_message=request.message, bot_response=bot_reply)
        return ChatResponse(response=bot_reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chatbot/history", response_model=List[ChatLogResponse])
async def get_chat_history(
    current_user: User = Depends(get_current_user)
):
    try:
        return get_chat_logs(user_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
