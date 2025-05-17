from fastapi import HTTPException
from datetime import datetime, timedelta
from app.schemas.user_schema import TokenPair
import jwt
import traceback

SECRET_KEY = "1234"
ALGORITHM = "HS256"

class JWTUtil:
    @staticmethod
    def generate_access_token(user_id: int) -> str:
        payload = {
            "sub": str(user_id),
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def generate_refresh_token(user_id: int) -> str:
        payload = {
            "sub": str(user_id),
            "exp": datetime.utcnow() + timedelta(days=7)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def generate_token_pair(user_id: int) -> TokenPair:
        access_token = JWTUtil.generate_access_token(user_id)
        refresh_token = JWTUtil.generate_refresh_token(user_id)
        return TokenPair(access_token=access_token, refresh_token=refresh_token)
    
    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    
    @staticmethod
    def generate_email_verification_token(email: str) -> str:
        payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_email_verification_token(token: str) -> str:
        decoded = JWTUtil.decode_token(token)
        email = decoded.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="토큰에 이메일 정보가 없습니다.")
        return email
    
    @staticmethod
    def generate_password_reset_token(email: str) -> str:
        payload = {
            "sub": email,
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def decode_password_reset_token(token: str) -> str:
        decoded = JWTUtil.decode_token(token)
        email = decoded.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="토큰에 이메일 정보가 없습니다.")
        return email