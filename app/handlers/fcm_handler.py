from fastapi import APIRouter, Depends

from app.handlers.user_handler import get_current_user
from app.models.user_model import User
from app.schemas.common_schema import ApiResponse
from app.schemas.user_schema import FCMTokenUpdate
from app.services.fcm_service import FcmService

router = APIRouter()

@router.patch("/users/fcm-token", response_model_exclude_none=True)
def update_fcm_token(
    req: FCMTokenUpdate,
    user: User=Depends(get_current_user),
    fcm_service: FcmService = Depends()
) -> ApiResponse[None]:
    fcm_service.update_user_fcm_token(user,req.fcm_token)
    return ApiResponse(message="FCM 토큰이 성공적으로 등록되었습니다.")