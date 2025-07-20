from fastapi import APIRouter, Depends, HTTPException
from openai import BaseModel

from app.handlers.user_handler import get_current_user
from app.models.user_model import User
from app.schemas.common_schema import ApiResponse
from app.schemas.user_schema import DirectFCMRequest, FCMTestRequest, FCMTokenUpdate
from app.services.fcm_service import FcmService
from app.utils.fcm_util import send_fcm_notification

router = APIRouter()

@router.patch("/users/fcm-token", response_model_exclude_none=True)
def update_fcm_token(
    req: FCMTokenUpdate,
    user: User=Depends(get_current_user),
    fcm_service: FcmService = Depends()
) -> ApiResponse[None]:
    fcm_service.update_user_fcm_token(user,req.fcm_token)
    return ApiResponse(message="FCM 토큰이 성공적으로 등록되었습니다.")

@router.post("/test/send-my-fcm")
async def send_my_fcm(
    request: FCMTestRequest,
    user: User = Depends(get_current_user)
):
    if not user.fcm_token:
        raise HTTPException(status_code=400, detail="해당 사용자에 저장된 FCM 토큰이 없습니다.")

    success = send_fcm_notification(
        token=user.fcm_token,
        title=request.title,
        body=request.body
    )
    if not success:
        raise HTTPException(status_code=500, detail="FCM 전송 실패")
    return {"message": "FCM 전송 성공"}

@router.post("/test/send-direct-fcm")
async def send_direct_fcm(request: DirectFCMRequest):
    success = send_fcm_notification(
        token=request.token,
        title=request.title,
        body=request.body
    )
    if not success:
        raise HTTPException(status_code=500, detail="FCM 전송 실패")
    return {"message": "FCM 전송 성공"}