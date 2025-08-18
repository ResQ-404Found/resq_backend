from typing import List, Optional
from sqlmodel import Session, select
from app.models.emergency_model import EmergencyContact, EmergencyLocation, EmergencyBroadcast, EmergencyBroadcastRecipient
from app.models.user_model import User
from app.services.fcm_service import FcmService

class EmergencyBroadcastService:
    def __init__(self, s: Session, user_id: int, fcm: FcmService):
        self.s = s; self.user_id = user_id; self.fcm = fcm

    # ... 위치 저장 동일 ...

    def _targets(self, ids: Optional[List[int]]) -> List[EmergencyContact]:
        q = select(EmergencyContact).where(EmergencyContact.user_id == self.user_id)
        if ids: q = q.where(EmergencyContact.id.in_(ids))
        else:   q = q.where(EmergencyContact.is_emergency == True)
        return self.s.exec(q).all()

    async def send(self, *, message: str, include_location: bool,
                   lat: Optional[float], lon: Optional[float], address: Optional[str],
                   contact_ids: Optional[List[int]]) -> EmergencyBroadcast:
        # ... 브로드캐스트/위치 생성 동일 ...
        # 메시지 조립
        # ...
        for c in self._targets(contact_ids):
            target = self.s.get(User, c.target_user_id)
            token = getattr(target, "fcm_token", None)
            if not token:
                self.s.add(EmergencyBroadcastRecipient(
                    broadcast_id=bc.id, contact_id=c.id, channel="push",
                    status="failed", error="missing_fcm_token"
                ))
                continue
            ok, msg_id, err = self.fcm.send_to_token(
                token=token, title=title, body=body,
                data={"type":"emergency","broadcast_id":str(bc.id),"contact_id":str(c.id)}
            )
            self.s.add(EmergencyBroadcastRecipient(
                broadcast_id=bc.id, contact_id=c.id, channel="push",
                status="sent" if ok else "failed", provider_message_id=msg_id, error=err
            ))
        self.s.commit()
        return bc
