from typing import List, Optional
from sqlmodel import Session, select
from app.models.emergency_model import EmergencyContact
from app.models.user_model import User

class EmergencyContactService:
    def __init__(self, s: Session, user_id: int):
        self.s = s
        self.user_id = user_id

    def list(self) -> List[dict]:
        rows = self.s.exec(select(EmergencyContact).where(EmergencyContact.user_id == self.user_id)
                           .order_by(EmergencyContact.id.desc())).all()
        # target 요약을 붙여서 반환
        out = []
        for r in rows:
            tu = self.s.get(User, r.target_user_id)
            out.append({
                "id": r.id,
                "target_user_id": r.target_user_id,
                "relation": r.relation,
                "is_emergency": r.is_emergency,
                "is_favorite": r.is_favorite,
                "target_username": getattr(tu, "username", None),
                "target_profile_imageURL": getattr(tu, "profile_imageURL", None),
            })
        return out

    def create(self, *, target_user_id: int, relation: Optional[str], is_emergency: bool) -> EmergencyContact:
        ec = EmergencyContact(user_id=self.user_id, target_user_id=target_user_id,
                              relation=relation, is_emergency=is_emergency)
        self.s.add(ec); self.s.commit(); self.s.refresh(ec)
        return ec

    def _get_owned(self, contact_id: int) -> Optional[EmergencyContact]:
        ec = self.s.get(EmergencyContact, contact_id)
        if ec and ec.user_id == self.user_id:
            return ec
        return None

    def update(self, contact_id: int, **patch) -> Optional[EmergencyContact]:
        ec = self._get_owned(contact_id)
        if not ec: return None
        for k, v in patch.items():
            if v is not None: setattr(ec, k, v)
        self.s.add(ec); self.s.commit(); self.s.refresh(ec)
        return ec

    def delete(self, contact_id: int) -> bool:
        ec = self._get_owned(contact_id)
        if not ec: return False
        self.s.delete(ec); self.s.commit()
        return True
