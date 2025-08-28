# app/utils/jwt_util.py
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from typing import Optional, Literal, Dict, Any
from sqlmodel import Session as SM_Session, select
from app.db.session import db_engine
from app.models.user_model import User, UserRole
import jwt
import os

SECRET_KEY = os.getenv("JWT_SECRET", "1234")   # 기존 상수도 유지, .env 우선
ALGORITHM = os.getenv("JWT_ALG", "HS256")

Role = Literal["USER", "ADMIN"]

class JWTUtil:
    @staticmethod
    def generate_access_token(user_id: int, role: Role) -> str:
        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def generate_refresh_token(user_id: int, role: Role) -> str:
        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def generate_token_pair(user: User):
        role_str: Role = (user.role.value if isinstance(user.role, UserRole) else str(user.role))
        access_token = JWTUtil.generate_access_token(user.id, role_str)   # type: ignore
        refresh_token = JWTUtil.generate_refresh_token(user.id, role_str) # type: ignore
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }


    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

def resolve_role_from_token_or_db(token: Optional[str]) -> Optional[Role]:
    """
    1) 토큰이 없으면 None
    2) 토큰 payload에 role 있으면 그대로 리턴
    3) role이 없으면 sub(user_id)로 DB 조회해서 role 복원(하위호환)
    4) 실패 시 None
    """
    if not token:
        return None
    try:
        payload = JWTUtil.decode_token(token)
        role = payload.get("role")
        if role in ("USER", "ADMIN"):
            return role  # type: ignore[return-value]
        # 하위호환: 예전 토큰(=role 없음) → DB에서 가져오기
        sub = payload.get("sub")
        if sub is None:
            return None
        uid = int(sub)
        with SM_Session(db_engine) as session:
            u = session.exec(select(User).where(User.id == uid)).first()
            if not u:
                return None
            if isinstance(u.role, UserRole):
                return u.role.value  # type: ignore[return-value]
            return str(u.role) if u.role in ("USER", "ADMIN") else None
    except Exception:
        return None
