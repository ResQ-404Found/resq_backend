from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db.session import get_db_session
from app.schemas.common_schema import ApiResponse
from app.core.redis import get_redis
from redis.asyncio import Redis
from app.services.email_service import EmailService

router = APIRouter()

@router.post("/request-verification-email")
async def request_verification_email(
    email: str,
    provider: str,
    email_service: EmailService = Depends()
) -> ApiResponse[None]:
    await email_service.request_verification(email, provider)
    return ApiResponse(message="인증 메일 발송 완료", data=None)

@router.get("/verify-email")
async def verify_email(
    token: str,
    email_service: EmailService = Depends()
) -> ApiResponse[None]:
    await email_service.verify_email_token(token)
    return ApiResponse(message="이메일 인증 완료", data=None)
