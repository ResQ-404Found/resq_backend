# app/handlers/purchase_handler.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.schemas.purchase_schemas import (
    VerifyPurchaseRequest,
    VerifyPurchaseResponse,
)
from app.services.purchase_service import GooglePlayService
from app.db.session import get_db_session 

router = APIRouter()

# 서비스계정 키 파일 경로는 환경에 맞게 조정
SERVICE_ACCOUNT_FILE = "파일 경로"

@router.post("purchase/verify", response_model=VerifyPurchaseResponse)
def verify_purchase(
    payload: VerifyPurchaseRequest,
    session: Session = Depends(get_db_session),
):
    service = GooglePlayService(service_account_file=SERVICE_ACCOUNT_FILE)
    try:
        purchase = service.verify_and_persist(
            session,
            package_name=payload.package_name,
            product_id=payload.product_id,
            purchase_token=payload.purchase_token,
            user_id=payload.user_id,
        )
        return VerifyPurchaseResponse(
            status="success",
            message="결제 검증 완료",
            order_id=purchase.order_id,
        )
    except RuntimeError as e:
        # 구글 검증 실패/상태 비정상 등
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 기타 예외
        raise HTTPException(status_code=500, detail=f"Internal Error: {e}")
