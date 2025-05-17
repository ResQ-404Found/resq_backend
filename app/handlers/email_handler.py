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

# 비밀번호 재설정 이메일 전송
@router.post("/request-password-reset", response_model_exclude_none=True)
async def request_password_reset(
    email: str,
    email_service: EmailService = Depends()
)->ApiResponse[None]:
    await email_service.request_password_reset(email)
    return ApiResponse(message="비밀번호 재설정 메일 발송 완료")

# 비밀번호 재설정
@router.post("/reset-password", response_model_exclude_none=True)
async def reset_password(
    req: ResetPassword,
    authorization: str = Header(...),
    user_service: UserService = Depends()
) -> ApiResponse[None]:
    token = authorization.replace("Bearer ", "")
    await user_service.reset_password(token, req.new_password)
    return ApiResponse(message="비밀번호 재설정 완료")

# 프론트에서 reset-password 페이지를 띄우기 전에 토큰 유효성 검사
@router.post("/verify-password-reset-token", response_model_exclude_none=True)
def verify_password_reset_token(authorization: str = Header(...)) -> ApiResponse[None]:
    try:
        token = authorization.replace("Bearer ", "")
        JWTUtil.decode_password_reset_token(token)
        return ApiResponse(message="토큰이 유효합니다.")
    except Exception:
        raise HTTPException(status_code=400, detail="토큰이 유효하지 않습니다.")