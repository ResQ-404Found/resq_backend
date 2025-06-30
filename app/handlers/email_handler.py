from fastapi import APIRouter, Depends
from app.schemas.common_schema import ApiResponse
from app.schemas.user_schema import ResetPassword
from app.services.email_service import EmailService
from app.services.user_service import UserService
from app.schemas.email_schema import EmailVerificationRequest, EmailVerificationCodeRequest, PasswordResetCodeRequest

router = APIRouter()

@router.post("/request-verification-email", response_model_exclude_none=True)
async def request_verification_email(
    req: EmailVerificationRequest,
    email_service: EmailService = Depends()
) -> ApiResponse[None]:
    """이메일 인증 요청 - 인증코드 발송"""
    await email_service.request_verification(req.email)
    return ApiResponse(message="인증 메일 발송 완료")

@router.post("/verify-email-code", response_model_exclude_none=True)
async def verify_email_code(
    req: EmailVerificationCodeRequest,
    email_service: EmailService = Depends()
) -> ApiResponse[None]:
    """이메일 인증코드 검증"""
    await email_service.verify_email_code(req.email, req.code)
    return ApiResponse(message="이메일 인증 완료")

@router.post("/request-password-reset", response_model_exclude_none=True)
async def request_password_reset(
    req: EmailVerificationRequest,
    email_service: EmailService = Depends()
) -> ApiResponse[None]:
    """비밀번호 재설정 인증코드 발송"""
    await email_service.request_password_reset(req.email)
    return ApiResponse(message="비밀번호 재설정 메일 발송 완료")

@router.post("/verify-password-reset-code", response_model_exclude_none=True)
async def verify_password_reset_code(
    req: PasswordResetCodeRequest,
    email_service: EmailService = Depends()
) -> ApiResponse[None]:
    """비밀번호 재설정 인증코드 검증"""
    await email_service.verify_password_reset_code(req.email, req.code)
    return ApiResponse(message="인증코드 검증 완료")

@router.post("/reset-password", response_model_exclude_none=True)
async def reset_password(
    req: ResetPassword,
    user_service: UserService = Depends()
) -> ApiResponse[None]:
    """비밀번호 재설정 (인증 완료 후)"""
    await user_service.reset_password_with_email(req.email, req.new_password)
    return ApiResponse(message="비밀번호 재설정 완료")