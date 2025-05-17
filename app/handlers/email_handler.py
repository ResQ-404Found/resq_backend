from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlmodel import Session
from app.db.session import get_db_session
from app.schemas.common_schema import ApiResponse
from app.core.redis import get_redis
from redis.asyncio import Redis
from app.schemas.user_schema import ResetPassword
from app.services.email_service import EmailService
from app.services.user_service import UserService
from app.utils.jwt_util import JWTUtil

router = APIRouter()

@router.post("/request-verification-email", response_model_exclude_none=True)
async def request_verification_email(
    email: str,
    email_service: EmailService = Depends()
) -> ApiResponse[None]:
    await email_service.request_verification(email)
    return ApiResponse(message="인증 메일 발송 완료")

# 토큰 유효성 검사 + 이메일 인증 완료 처리
@router.post("/verify-email-token", response_model_exclude_none=True)
async def verify_email(
    authorization: str = Header(...),
    email_service: EmailService = Depends()
) -> ApiResponse[None]:
    token = authorization.replace("Bearer ", "")
    await email_service.verify_email_token(token)
    return ApiResponse(message="이메일 인증 완료")
