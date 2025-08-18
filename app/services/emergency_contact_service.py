from typing import Optional, List
from sqlmodel import Session, select
from app.models.emergency_model import EmergencyContact
from app.models.user_model import User
from app.models.friend_model import FriendRequest, FriendStatus

class EmergencyContactService:
    def __init__(self, s: Session, user_id: int):
        self.s = s
        self.user_id = user_id

    def list(self) -> List[dict]:
        rows = self.s.exec(
            select(EmergencyContact)
            .where(EmergencyContact.user_id == self.user_id)
            .order_by(EmergencyContact.id.desc())
        ).all()
        out: List[dict] = []
        for r in rows:
            tu = self.s.get(User, r.target_user_id)
            out.append({
                "id": r.id,
                "target_user_id": r.target_user_id,
                "relation": r.relation,
                "is_emergency": True,  # 존재=TRUE
                "target_username": getattr(tu, "username", None),
                "target_profile_imageURL": getattr(tu, "profile_imageURL", None),
            })
        return out

    def _is_friend(self, other_user_id: int) -> bool:
        q = select(FriendRequest).where(
            (FriendRequest.status == FriendStatus.ACCEPTED) &
            (
                ((FriendRequest.requester_id == self.user_id) & (FriendRequest.addressee_id == other_user_id)) |
                ((FriendRequest.requester_id == other_user_id) & (FriendRequest.addressee_id == self.user_id))
            )
        )
        return self.s.exec(q).first() is not None

    # enabled=True → 생성, False → 삭제
    def set_emergency(self, friend_user_id: int, enabled: bool, relation: Optional[str] = None):
        if not self._is_friend(friend_user_id):
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
            ec = EmergencyContact(
                user_id=self.user_id,
                target_user_id=friend_user_id,
                relation=relation,
            )
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
