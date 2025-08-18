# app/services/emergency_service.py
from typing import Optional, List, Dict
from datetime import datetime
from sqlmodel import Session, select
from starlette.concurrency import run_in_threadpool

from app.models.emergency_model import (
    EmergencyContact, EmergencyLocation, EmergencyBroadcast, EmergencyBroadcastRecipient
)
from app.models.user_model import User
from app.models.friend_model import FriendRequest, FriendStatus
from app.schemas.emergency_schema import EmergencyBroadcastCreate
from app.utils.fcm_util import send_fcm_notification

class EmergencyService:
    def __init__(self, s: Session, user_id: int):
        self.s = s
        self.user_id = user_id

    # ---------- Contacts ----------
    def _is_friend(self, other_user_id: int) -> bool:
        q = select(FriendRequest).where(
            (FriendRequest.status == FriendStatus.ACCEPTED) &
            (
                ((FriendRequest.requester_id == self.user_id) & (FriendRequest.addressee_id == other_user_id)) |
                ((FriendRequest.requester_id == other_user_id) & (FriendRequest.addressee_id == self.user_id))
            )
        )
        return self.s.exec(q).first() is not None

    def list_contacts(self) -> List[Dict]:
        rows = self.s.exec(
            select(EmergencyContact)
            .where(EmergencyContact.user_id == self.user_id)
            .order_by(EmergencyContact.id.desc())
        ).all()
        out: List[Dict] = []
        for r in rows:
            tu = self.s.get(User, r.target_user_id)
            out.append({
                "id": r.id,
                "target_user_id": r.target_user_id,
                "relation": r.relation,
                "is_emergency": True,
                "target_username": getattr(tu, "username", None),
                "target_profile_imageURL": getattr(tu, "profile_imageURL", None),
            })
        return out

    def set_contact(self, friend_user_id: int, enabled: bool, relation: Optional[str] = None):
        """친구를 비상연락 대상으로 등록/해제 (enabled=True → 생성, False → 삭제)"""
        if enabled and not self._is_friend(friend_user_id):
            raise ValueError("친구가 아닌 사용자입니다.")

        exists = self.s.exec(select(EmergencyContact).where(
            (EmergencyContact.user_id == self.user_id) &
            (EmergencyContact.target_user_id == friend_user_id)
        )).first()

        if enabled:
            if exists:
                if relation is not None and relation != exists.relation:
                    exists.relation = relation
                    self.s.add(exists); self.s.commit(); self.s.refresh(exists)
                return exists
            ec = EmergencyContact(user_id=self.user_id, target_user_id=friend_user_id, relation=relation)
            self.s.add(ec); self.s.commit(); self.s.refresh(ec)
            return ec
        else:
            if exists:
                self.s.delete(exists); self.s.commit()
            return None

    def selected_user_id_set(self) -> set[int]:
        ids = self.s.exec(select(EmergencyContact.target_user_id).where(
            EmergencyContact.user_id == self.user_id
        )).all()
        return set([t[0] if isinstance(t, tuple) else t for t in ids])

    # ---------- Broadcast ----------
    def _save_location(self, lat: float, lon: float, address: Optional[str]) -> int:
        loc = EmergencyLocation(user_id=self.user_id, lat=lat, lon=lon, address=address)
        self.s.add(loc); self.s.commit(); self.s.refresh(loc)
        return loc.id

    def _target_contacts(self, ids: Optional[List[int]]) -> List[EmergencyContact]:
        q = select(EmergencyContact).where(EmergencyContact.user_id == self.user_id)
        if ids:
            q = q.where(EmergencyContact.id.in_(ids))
        # ids가 없으면 등록된 전체(행 존재 = is_emergency True)
        return self.s.exec(q).all()

    async def send_broadcast(self, payload: EmergencyBroadcastCreate) -> EmergencyBroadcast:
        # 위치 저장(옵션)
        loc_id = None
        if payload.include_location and payload.lat is not None and payload.lon is not None:
            loc_id = self._save_location(payload.lat, payload.lon, payload.address)

        # 브로드캐스트 생성
        bc = EmergencyBroadcast(
            user_id=self.user_id,
            message=payload.message,
            include_location=payload.include_location,
            location_id=loc_id
        )
        self.s.add(bc); self.s.commit(); self.s.refresh(bc)

        # 메시지 조립
        suffix = ""
        if payload.include_location and loc_id:
            loc = self.s.get(EmergencyLocation, loc_id)
            suffix = f"\n위치: https://maps.google.com/?q={loc.lat},{loc.lon}"
        title = "[긴급] 위치 공유"
        body = f"{payload.message}{suffix}"

        # 대상 전송
        contacts = self._target_contacts(payload.contact_ids)
        for c in contacts:
            target = self.s.get(User, c.target_user_id)
            token = getattr(target, "fcm_token", None)

            if not token:
                self.s.add(EmergencyBroadcastRecipient(
                    broadcast_id=bc.id, contact_id=c.id, channel="push",
                    status="failed", error="missing_fcm_token"
                ))
                continue

            ok: bool = await run_in_threadpool(send_fcm_notification, token, title, body)
            self.s.add(EmergencyBroadcastRecipient(
                broadcast_id=bc.id, contact_id=c.id, channel="push",
                status="sent" if ok else "failed"
            ))

        self.s.commit()
        return bc
# app/services/emergency_service.py
from typing import Optional, List, Dict
from datetime import datetime
from sqlmodel import Session, select
from starlette.concurrency import run_in_threadpool

from app.models.emergency_model import (
    EmergencyContact, EmergencyLocation, EmergencyBroadcast, EmergencyBroadcastRecipient
)
from app.models.user_model import User
from app.models.friend_model import FriendRequest, FriendStatus
from app.schemas.emergency_schema import EmergencyBroadcastCreate
from app.utils.fcm_util import send_fcm_notification

class EmergencyService:
    def __init__(self, s: Session, user_id: int):
        self.s = s
        self.user_id = user_id

    # ---------- Contacts ----------
    def _is_friend(self, other_user_id: int) -> bool:
        q = select(FriendRequest).where(
            (FriendRequest.status == FriendStatus.ACCEPTED) &
            (
                ((FriendRequest.requester_id == self.user_id) & (FriendRequest.addressee_id == other_user_id)) |
                ((FriendRequest.requester_id == other_user_id) & (FriendRequest.addressee_id == self.user_id))
            )
        )
        return self.s.exec(q).first() is not None

    def list_contacts(self) -> List[Dict]:
        rows = self.s.exec(
            select(EmergencyContact)
            .where(EmergencyContact.user_id == self.user_id)
            .order_by(EmergencyContact.id.desc())
        ).all()
        out: List[Dict] = []
        for r in rows:
            tu = self.s.get(User, r.target_user_id)
            out.append({
                "id": r.id,
                "target_user_id": r.target_user_id,
                "relation": r.relation,
                "is_emergency": True,
                "target_username": getattr(tu, "username", None),
                "target_profile_imageURL": getattr(tu, "profile_imageURL", None),
            })
        return out

    def set_contact(self, friend_user_id: int, enabled: bool, relation: Optional[str] = None):
        """친구를 비상연락 대상으로 등록/해제 (enabled=True → 생성, False → 삭제)"""
        if enabled and not self._is_friend(friend_user_id):
            raise ValueError("친구가 아닌 사용자입니다.")

        exists = self.s.exec(select(EmergencyContact).where(
            (EmergencyContact.user_id == self.user_id) &
            (EmergencyContact.target_user_id == friend_user_id)
        )).first()

        if enabled:
            if exists:
                if relation is not None and relation != exists.relation:
                    exists.relation = relation
                    self.s.add(exists); self.s.commit(); self.s.refresh(exists)
                return exists
            ec = EmergencyContact(user_id=self.user_id, target_user_id=friend_user_id, relation=relation)
            self.s.add(ec); self.s.commit(); self.s.refresh(ec)
            return ec
        else:
            if exists:
                self.s.delete(exists); self.s.commit()
            return None

    def selected_user_id_set(self) -> set[int]:
        ids = self.s.exec(select(EmergencyContact.target_user_id).where(
            EmergencyContact.user_id == self.user_id
        )).all()
        return set([t[0] if isinstance(t, tuple) else t for t in ids])

    # ---------- Broadcast ----------
    def _save_location(self, lat: float, lon: float, address: Optional[str]) -> int:
        loc = EmergencyLocation(user_id=self.user_id, lat=lat, lon=lon, address=address)
        self.s.add(loc); self.s.commit(); self.s.refresh(loc)
        return loc.id

    def _target_contacts(self, ids: Optional[List[int]]) -> List[EmergencyContact]:
        q = select(EmergencyContact).where(EmergencyContact.user_id == self.user_id)
        if ids:
            q = q.where(EmergencyContact.id.in_(ids))
        # ids가 없으면 등록된 전체(행 존재 = is_emergency True)
        return self.s.exec(q).all()

    async def send_broadcast(self, payload: EmergencyBroadcastCreate) -> EmergencyBroadcast:
        # 위치 저장(옵션)
        loc_id = None
        if payload.include_location and payload.lat is not None and payload.lon is not None:
            loc_id = self._save_location(payload.lat, payload.lon, payload.address)

        # 브로드캐스트 생성
        bc = EmergencyBroadcast(
            user_id=self.user_id,
            message=payload.message,
            include_location=payload.include_location,
            location_id=loc_id
        )
        self.s.add(bc); self.s.commit(); self.s.refresh(bc)

        # 메시지 조립
        suffix = ""
        if payload.include_location and loc_id:
            loc = self.s.get(EmergencyLocation, loc_id)
            suffix = f"\n위치: https://maps.google.com/?q={loc.lat},{loc.lon}"
        title = "[긴급] 위치 공유"
        body = f"{payload.message}{suffix}"

        # 대상 전송
        contacts = self._target_contacts(payload.contact_ids)
        for c in contacts:
            target = self.s.get(User, c.target_user_id)
            token = getattr(target, "fcm_token", None)

            if not token:
                self.s.add(EmergencyBroadcastRecipient(
                    broadcast_id=bc.id, contact_id=c.id, channel="push",
                    status="failed", error="missing_fcm_token"
                ))
                continue

            ok: bool = await run_in_threadpool(send_fcm_notification, token, title, body)
            self.s.add(EmergencyBroadcastRecipient(
                broadcast_id=bc.id, contact_id=c.id, channel="push",
                status="sent" if ok else "failed"
            ))

        self.s.commit()
        return bc
