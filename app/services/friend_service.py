from typing import List, Iterable, Dict
from datetime import datetime
from sqlmodel import Session, select

from app.models.user_model import User
from app.models.friend_model import FriendRequest, FriendStatus
from app.models.emergency_model import EmergencyContact as EmergencyContactModel  # 모델은 별칭으로
from app.services.emergency_service import EmergencyService  # 비상연락 서비스

class FriendService:
    def __init__(self, s: Session, user_id: int):
        self.s = s
        self.user_id = user_id

    # 닉네임 검색
    def search_users(self, username: str, limit: int = 10) -> List[User]:
        q = (select(User)
             .where(User.username.ilike(f"%{username}%"))
             .where(User.id != self.user_id)
             .limit(limit))
        return self.s.exec(q).all()

    # 친구 요청 보내기
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
            if same.status in (FriendStatus.REJECTED, FriendStatus.CANCELED):
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
                return reverse

        fr = FriendRequest(
            requester_id=self.user_id,
            addressee_id=target.id,
            status=FriendStatus.PENDING
        )
        self.s.add(fr); self.s.commit(); self.s.refresh(fr)
        return fr

    # 친구 수락 (양방향 비상연락 자동 등록)
    def accept(self, request_id: int) -> FriendRequest:
        fr = self.s.get(FriendRequest, request_id)
        if not fr or fr.addressee_id != self.user_id or fr.status != FriendStatus.PENDING:
            raise ValueError("수락할 수 없는 요청입니다.")

        fr.status = FriendStatus.ACCEPTED
        fr.responded_at = datetime.utcnow()
        self.s.add(fr); self.s.commit(); self.s.refresh(fr)

        EmergencyService(self.s, fr.requester_id).set_contact(fr.addressee_id, True)
        EmergencyService(self.s, fr.addressee_id).set_contact(fr.requester_id, True)
        self.s.commit()
        return fr

    # 내부: 비상연락 행 삭제
    def _delete_emergency_contact(self, owner_id: int, target_id: int):
        ec = self.s.exec(select(EmergencyContactModel).where(
            (EmergencyContactModel.user_id == owner_id) &
            (EmergencyContactModel.target_user_id == target_id)
        )).first()
        if ec:
            self.s.delete(ec)

    # 친구 삭제(양방향 비상연락도 삭제)
    def unfriend(self, friend_user_id: int) -> bool:
        fr = self.s.exec(select(FriendRequest).where(
            (FriendRequest.status == FriendStatus.ACCEPTED) &
            (
                ((FriendRequest.requester_id == self.user_id) & (FriendRequest.addressee_id == friend_user_id)) |
                ((FriendRequest.requester_id == friend_user_id) & (FriendRequest.addressee_id == self.user_id))
            )
        )).first()
        if not fr:
            raise ValueError("현재 친구 상태가 아닙니다.")

        self._delete_emergency_contact(self.user_id, friend_user_id)
        self._delete_emergency_contact(friend_user_id, self.user_id)

        self.s.delete(fr)
        self.s.commit()
        return True

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
        if ids:
            users = {u.id: u for u in self.s.exec(select(User).where(User.id.in_(ids))).all()}

        out: List[dict] = []
        for r in rows:
            out.append({
                "id": r.id,
                "requester_id": r.requester_id,
                "addressee_id": r.addressee_id,
                "status": str(r.status),
                "requester_username": users.get(r.requester_id).username if users.get(r.requester_id) else None,
                "addressee_username": users.get(r.addressee_id).username if users.get(r.addressee_id) else None,
            })
        return out

    # 친구 목록 + 내 비상연락 여부 플래그
    def list_friends_with_emergency_flag(self) -> List[dict]:
        rows = self.s.exec(select(FriendRequest).where(
            (FriendRequest.status == FriendStatus.ACCEPTED) &
            ((FriendRequest.requester_id == self.user_id) | (FriendRequest.addressee_id == self.user_id))
        )).all()

        friend_ids = [r.addressee_id if r.requester_id == self.user_id else r.requester_id for r in rows]
        if not friend_ids:
            return []

        users = self.s.exec(select(User).where(User.id.in_(friend_ids))).all()
        emergency_ids = EmergencyService(self.s, self.user_id).selected_user_id_set()

        out: List[dict] = []
        for u in users:
            out.append({
                "id": u.id,
                "target_user_id": u.id,
                "relation": None,
                "is_emergency": (u.id in emergency_ids),
                "target_username": u.username,
                "target_profile_imageURL": u.profile_imageURL,
            })
        return out
