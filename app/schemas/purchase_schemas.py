# app/schemas/purchase_schema.py
from pydantic import BaseModel, Field
from typing import Optional

class VerifyPurchaseRequest(BaseModel):
    purchase_token: str = Field(..., description="Google Play에서 받은 purchaseToken")
    product_id: str = Field("donation_1000", description="상품 ID (콘솔에 등록한 ID)")
    package_name: str = Field("com.example.yourapp", description="앱 패키지명")
    user_id: Optional[int] = Field(None, description="로그인 사용자의 ID (선택)")

class VerifyPurchaseResponse(BaseModel):
    status: str
    message: str
    order_id: Optional[str] = None
