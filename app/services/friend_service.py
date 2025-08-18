from typing import List, Optional, Iterable, Dict  # ← Iterable, Dict 추가
from datetime import datetime
from sqlmodel import Session, select
from app.models.user_model import User
from app.models.friend_model import FriendRequest, FriendStatus
from app.models.emergency_model import EmergencyContact

class FriendService:
    def __init__(self, s: Session, user_id: int):
        self.s = s
        self.user_id = user_id
  
    def search_users(self, username: str, limit: int = 10) -> List[User]:
        q = (select(User)
             .where(User.username.ilike(f"%{username}%"))
             .where(User.id != self.user_id)               
             .limit(limit))
        return self.s.exec(q).all()

    def send_request(self, target_username: str) -> FriendRequest:
        target = self.s.exec(select(User).where(User.username == target_username)).first()
        if not target:
            raise ValueError("해당 닉네임의 사용자가 없습니다.")
        if target.id == self.user_id:
            raise ValueError("자기 자신에게는 요청할 수 없습니다.")
        
        same = self.s.exec(select(FriendRequest).where(
            (FriendRequest.requester_id == self.user_id) &
            (FriendRequest.addressee_id == target.id)
        )).first()

        if same:
            if same.status == FriendStatus.PENDING:
                return same 
            if same.status == FriendStatus.ACCEPTED:
                return same  
            if same.status in (FriendStatus.REJECTED, FriendStatus.CANCELED): #재요청
                same.status = FriendStatus.PENDING
                same.responded_at = None
                self.s.add(same); self.s.commit(); self.s.refresh(same)
                return same

        reverse = self.s.exec(select(FriendRequest).where(
            (FriendRequest.requester_id == target.id) &
            (FriendRequest.addressee_id == self.user_id)
        )).first()

        if reverse:
            if reverse.status == FriendStatus.PENDING:
                raise ValueError("상대방의 친구 요청이 대기 중입니다. 먼저 수락하세요.")
            if reverse.status == FriendStatus.ACCEPTED:
                return reverse  # 이미 친구

        fr = FriendRequest(
            requester_id=self.user_id,
            addressee_id=target.id,
            status=FriendStatus.PENDING
        )
        self.s.add(fr); self.s.commit(); self.s.refresh(fr)
        return fr

    def accept(self, request_id: int) -> FriendRequest:
        fr = self.s.get(FriendRequest, request_id)
        if not fr or fr.addressee_id != self.user_id or fr.status != FriendStatus.PENDING:
            raise ValueError("수락할 수 없는 요청입니다.")
        fr.status = FriendStatus.ACCEPTED
        fr.responded_at = datetime.utcnow()
        self.s.add(fr); self.s.commit()

        self._upsert_contact(fr.requester_id, fr.addressee_id)  
        self._upsert_contact(fr.addressee_id, fr.requester_id)  
        self.s.commit()
        self.s.refresh(fr)
        return fr

    def reject(self, request_id: int) -> FriendRequest:
        fr = self.s.get(FriendRequest, request_id)
        if not fr or fr.addressee_id != self.user_id or fr.status != FriendStatus.PENDING:
            raise ValueError("거절할 수 없는 요청입니다.")
        fr.status = FriendStatus.REJECTED
        fr.responded_at = datetime.utcnow()
        self.s.add(fr); self.s.commit(); self.s.refresh(fr)
        return fr

    def cancel(self, request_id: int) -> FriendRequest:
        fr = self.s.get(FriendRequest, request_id)
        if not fr or fr.requester_id != self.user_id or fr.status != FriendStatus.PENDING:
            raise ValueError("취소할 수 없는 요청입니다.")
        fr.status = FriendStatus.CANCELED
        fr.responded_at = datetime.utcnow()
        self.s.add(fr); self.s.commit(); self.s.refresh(fr)
        return fr

    def list_friends(self) -> List[User]:
        rows = self.s.exec(select(FriendRequest).where(
            (FriendRequest.status == FriendStatus.ACCEPTED) &
            ((FriendRequest.requester_id == self.user_id) | (FriendRequest.addressee_id == self.user_id))
        )).all()
        friend_ids = [r.addressee_id if r.requester_id == self.user_id else r.requester_id for r in rows]
        if not friend_ids:
            return []
        return self.s.exec(select(User).where(User.id.in_(friend_ids))).all()

    def list_incoming_read(self) -> List[dict]:
        rows = self.s.exec(select(FriendRequest).where(
            (FriendRequest.addressee_id == self.user_id) &
            (FriendRequest.status == FriendStatus.PENDING)
        )).all()
        return self._attach_usernames(rows)

    def list_outgoing_read(self) -> List[dict]:
        rows = self.s.exec(select(FriendRequest).where(
            (FriendRequest.requester_id == self.user_id) &
            (FriendRequest.status == FriendStatus.PENDING)
        )).all()
        return self._attach_usernames(rows)

    def _attach_usernames(self, rows: Iterable[FriendRequest]) -> List[dict]:
        ids: set[int] = set()
        for r in rows:
            ids.add(r.requester_id)
            ids.add(r.addressee_id)

        users: Dict[int, User] = {}
        if ids:  # ← 빈 in_ 가드
            users = {u.id: u for u in self.s.exec(select(User).where(User.id.in_(ids))).all()}

        out: List[dict] = []
        for r in rows:
            out.append({
                "id": r.id,
                "requester_id": r.requester_id,
                "addressee_id": r.addressee_id,
                "status": str(r.status),  # ← 문자열로 보장
                "requester_username": users.get(r.requester_id).username if users.get(r.requester_id) else None,
                "addressee_username": users.get(r.addressee_id).username if users.get(r.addressee_id) else None,
            })
        return out

    def _upsert_contact(self, owner_id: int, target_id: int):
        exists = self.s.exec(select(EmergencyContact).where(
            (EmergencyContact.user_id == owner_id) & (EmergencyContact.target_user_id == target_id)
        )).first()
        if not exists:
            ec = EmergencyContact(user_id=owner_id, target_user_id=target_id, relation="친구", is_emergency=False)
            self.s.add(ec)
