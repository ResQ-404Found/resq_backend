from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.chatbot_schema import ChatRequest, ChatResponse, ChatLogResponse
from app.services.chatbot_service import (
    get_disaster_response, get_counseling_response,
    save_chat_log, get_chat_logs
)
from app.models.user_model import User
from app.handlers.user_handler import get_current_user

router = APIRouter()

@router.post("/chatbot/disaster", response_model=ChatResponse)
async def chat_with_disaster_bot(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        bot_reply = get_disaster_response(request.message)
        save_chat_log(current_user.id, request.message, bot_reply, "disaster")
        return ChatResponse(response=bot_reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chatbot/disaster/history", response_model=List[ChatLogResponse])
async def get_disaster_history(current_user: User = Depends(get_current_user)):
    try:
        return get_chat_logs(current_user.id, "disaster")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chatbot/counseling", response_model=ChatResponse)
async def chat_with_counseling_bot(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        bot_reply = get_counseling_response(request.message)
        save_chat_log(current_user.id, request.message, bot_reply, "counseling")
        return ChatResponse(response=bot_reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chatbot/counseling/history", response_model=List[ChatLogResponse])
async def get_counseling_history(current_user: User = Depends(get_current_user)):
    try:
        return get_chat_logs(current_user.id, "counseling")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
