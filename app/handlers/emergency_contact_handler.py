from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_db_session
from app.handlers.user_handler import get_current_user
from app.schemas.emergency_schema import EmergencyContactCreate, EmergencyContactRead, EmergencyContactUpdate
from app.services.emergency_contact_service import EmergencyContactService

router = APIRouter(prefix="/api/emergency/contacts", tags=["EmergencyContacts"])

@router.get("", response_model=List[EmergencyContactRead])
def list_contacts(s: Session = Depends(get_db_session), user=Depends(get_current_user)):
    # 서비스는 dict로 target 요약까지 돌려주므로 스키마에 매핑됨
    return EmergencyContactService(s, user.id).list()

@router.post("", response_model=EmergencyContactRead, status_code=201)
def create_contact(payload: EmergencyContactCreate, s: Session = Depends(get_db_session), user=Depends(get_current_user)):
    c = EmergencyContactService(s, user.id).create(**payload.dict())
    # 프론트 편의상 다시 조회해서 target 요약 포함해 반환
    return EmergencyContactService(s, user.id).list()[0]

@router.patch("/{contact_id}", response_model=EmergencyContactRead)
def update_contact(contact_id: int, payload: EmergencyContactUpdate, s: Session = Depends(get_db_session), user=Depends(get_current_user)):
    svc = EmergencyContactService(s, user.id)
    c = svc.update(contact_id, **payload.dict(exclude_none=True))
    if not c:
        raise HTTPException(404, "Not found")
    # 변경 반영된 항목만 찾아서 리턴
    for row in svc.list():
        if row["id"] == contact_id: return row
    raise HTTPException(404, "Not found")

@router.delete("/{contact_id}", status_code=204)
def delete_contact(contact_id: int, s: Session = Depends(get_db_session), user=Depends(get_current_user)):
    ok = EmergencyContactService(s, user.id).delete(contact_id)
    if not ok:
        raise HTTPException(404, "Not found")
