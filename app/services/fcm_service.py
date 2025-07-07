from fastapi import Depends
from sqlmodel import Session
from app.db.session import get_db_session
from app.models.user_model import User

class FcmService():
    def __init__(self, session: Session=Depends(get_db_session)):
        self.session = session
        
    def update_user_fcm_token(self, user: User, fcm_token: str):
        if not fcm_token:
            raise ValueError("FCM 토큰이 비어있습니다.")
        user.fcm_token = fcm_token
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return True