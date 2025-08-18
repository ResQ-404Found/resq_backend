# app/models/purchase.py
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Purchase(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # 누구의 후원인지 연결
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    package_name: str = Field(index=True)
    product_id: str = Field(index=True)

    # 구글에서 받은 토큰
    purchase_token: str = Field(unique=True, index=True)

    # 검증 결과
    purchase_state: int = Field(default=0)          # 0=구매완료
    consumption_state: Optional[int] = Field(default=None)
    acknowledged: Optional[bool] = Field(default=None)

    order_id: Optional[str] = Field(default=None, index=True)
    purchase_time: Optional[datetime] = Field(default=None)

    # 원문 응답 보관(디버깅용)
    raw_response: Optional[str] = Field(default=None)
