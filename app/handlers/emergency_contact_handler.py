from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_db_session
from app.handlers.user_handler import get_current_user
from app.schemas.emergency_schema import EmergencyContactCreate, EmergencyContactRead, EmergencyContactUpdate
from app.services.emergency_contact_service import EmergencyContactService

router = APIRouter(prefix="/emergency/contacts")

@router.get("", response_model=List[EmergencyContactRead])
def list_contacts(s: Session = Depends(get_db_session), user=Depends(get_current_user)):
    # 서비스는 dict로 target 요약까지 돌려주므로 스키마에 매핑됨
    return EmergencyContactService(s, user.id).list()
