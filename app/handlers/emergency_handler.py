# app/handlers/emergency_handler.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_db_session
from app.handlers.user_handler import get_current_user
from app.schemas.emergency_schema import (
    EmergencyContactRead,
    EmergencyBroadcastCreate, EmergencyBroadcastRead,
    EmergencyBroadcastSummaryRead, EmergencyBroadcastDetailRead,  
)
from app.services.emergency_service import EmergencyService

router = APIRouter(prefix="/emergency")

# 비상연락처 목록
@router.get("/contacts", response_model=List[EmergencyContactRead])
def list_contacts(s: Session = Depends(get_db_session), user=Depends(get_current_user)):
    return EmergencyService(s, user.id).list_contacts()

# 브로드캐스트 전송
@router.post("/broadcasts", response_model=EmergencyBroadcastRead, status_code=201)
async def send_broadcast(payload: EmergencyBroadcastCreate,
                         s: Session = Depends(get_db_session),
                         user=Depends(get_current_user)):
    return await EmergencyService(s, user.id).send_broadcast(payload)

# 브로드캐스트 집계 목록
@router.get("/broadcasts", response_model=List[EmergencyBroadcastSummaryRead])
def list_broadcasts(limit: int = 20,
                    s: Session = Depends(get_db_session),
                    user=Depends(get_current_user)):
    return EmergencyService(s, user.id).list_broadcasts(limit=limit)

# 특정 브로드캐스트 상세
@router.get("/broadcasts/{broadcast_id}", response_model=EmergencyBroadcastDetailRead)
def get_broadcast_detail(broadcast_id: int,
                         s: Session = Depends(get_db_session),
                         user=Depends(get_current_user)):
    try:
        return EmergencyService(s, user.id).get_broadcast_detail(broadcast_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
