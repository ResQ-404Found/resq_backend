# app/services/emergency_broadcast_service.py
from typing import List, Optional
from sqlmodel import Session, select
from starlette.concurrency import run_in_threadpool

from app.models.emergency_model import (
    EmergencyContact, EmergencyLocation, EmergencyBroadcast, EmergencyBroadcastRecipient
)
from app.models.user_model import User
from app.utils.fcm_util import send_fcm_notification 

class EmergencyBroadcastService:
    def __init__(self, s: Session, user_id: int):
        self.s = s
        self.user_id = user_id

    def _save_loc(self, lat: float, lon: float, address: Optional[str]) -> int:
        loc = EmergencyLocation(user_id=self.user_id, lat=lat, lon=lon, address=address)
        self.s.add(loc); self.s.commit(); self.s.refresh(loc)
        return loc.id

    def _targets(self, ids: Optional[List[int]]) -> List[EmergencyContact]:
        q = select(EmergencyContact).where(EmergencyContact.user_id == self.user_id)
        if ids:
            q = q.where(EmergencyContact.id.in_(ids))
        # else: 행 존재 == is_emergency True
        return self.s.exec(q).all()


    async def send(self, *, message: str, include_location: bool,
                   lat: Optional[float], lon: Optional[float], address: Optional[str],
                   contact_ids: Optional[List[int]]) -> EmergencyBroadcast:

        # 위치 저장(옵션)
        loc_id = None
        if include_location and lat is not None and lon is not None:
            loc_id = self._save_loc(lat, lon, address)

        # 브로드캐스트 생성
        bc = EmergencyBroadcast(
            user_id=self.user_id, message=message,
            include_location=include_location, location_id=loc_id
        )
        self.s.add(bc); self.s.commit(); self.s.refresh(bc)

        # 메시지 조립
        suffix = ""
        if include_location and loc_id:
            loc = self.s.get(EmergencyLocation, loc_id)
            suffix = f"\n위치: https://maps.google.com/?q={loc.lat},{loc.lon}"
        title = "[긴급] 위치 공유"
        body  = f"{message}{suffix}"

        # 대상 전송
        for c in self._targets(contact_ids):
            target = self.s.get(User, c.target_user_id)
            token = getattr(target, "fcm_token", None)

            if not token:
                self.s.add(EmergencyBroadcastRecipient(
                    broadcast_id=bc.id, contact_id=c.id, channel="push",
                    status="failed", error="missing_fcm_token"
                ))
                continue

            # 동기 전송 유틸을 스레드풀로
            ok: bool = await run_in_threadpool(send_fcm_notification, token, title, body)

            self.s.add(EmergencyBroadcastRecipient(
                broadcast_id=bc.id, contact_id=c.id, channel="push",
                status="sent" if ok else "failed"
            ))

        self.s.commit()
        return bc
