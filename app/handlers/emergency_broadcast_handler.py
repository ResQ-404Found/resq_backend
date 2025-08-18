from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import Any
from app.db.session import get_db_session
from app.handlers.user_handler import get_current_user
from app.models.emergency_model import EmergencyBroadcastRecipient
from app.schemas.emergency_schema import EmergencyBroadcastCreate, EmergencyBroadcastRead
from app.services.emergency_broadcast_service import EmergencyBroadcastService
from app.services.fcm_service import FcmService

router = APIRouter(prefix="/api/emergency/broadcasts", tags=["EmergencyBroadcasts"])
_fcm = FcmService()

@router.post("", response_model=EmergencyBroadcastRead, status_code=201)
async def send_broadcast(payload: EmergencyBroadcastCreate,
                         s: Session = Depends(get_db_session),
                         user = Depends(get_current_user)):
    svc = EmergencyBroadcastService(s, user.id, _fcm)
    bc = await svc.send(**payload.dict())
    return bc

@router.get("/{broadcast_id}/recipients")
def list_recipients(broadcast_id: int,
                    s: Session = Depends(get_db_session),
                    user = Depends(get_current_user)) -> list[dict[str, Any]]:
    rows = s.exec(select(EmergencyBroadcastRecipient)
                  .where(EmergencyBroadcastRecipient.broadcast_id == broadcast_id)).all()
    return [{"contact_id": r.contact_id, "channel": r.channel, "status": r.status, "error": r.error} for r in rows]
