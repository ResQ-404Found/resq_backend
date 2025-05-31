from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from app.db.session import get_db_session
from app.services.user_service import UserService
from app.utils.jwt_util import JWTUtil
from app.models.user_model import User

bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_db_session)
) -> User:
    token = credentials.credentials
    try:
        payload = JWTUtil.decode_token(token)
    except HTTPException as e:
        raise e

    user_id = int(payload.get("sub"))
    user_service = UserService(db=session)
    return user_service.get_user_by_id(user_id)
