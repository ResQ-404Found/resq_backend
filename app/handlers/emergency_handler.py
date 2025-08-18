# app/handlers/emergency_handler.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_db_session
from app.handlers.user_handler import get_current_user
from app.schemas.emergency_schema import (
    EmergencyContactRead, EmergencyContactUpsert,
    EmergencyBroadcastCreate, EmergencyBroadcastRead
)
from app.services.emergency_service import EmergencyService

router = APIRouter(prefix="/emergency")

# ----- Contacts -----
@router.get("/contacts", response_model=List[EmergencyContactRead])
def list_contacts(s: Session = Depends(get_db_session), user=Depends(get_current_user)):
    return EmergencyService(s, user.id).list_contacts()

@router.post("/broadcasts", response_model=EmergencyBroadcastRead, status_code=201)
async def send_broadcast(payload: EmergencyBroadcastCreate,
                         s: Session = Depends(get_db_session),
                         user=Depends(get_current_user)):
    bc = await EmergencyService(s, user.id).send_broadcast(payload)
    return bc
