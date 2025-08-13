# app/services/google_play_service.py
import json
from datetime import datetime, timezone
from typing import Optional

import requests
from sqlmodel import Session, select
from google.oauth2 import service_account
import google.auth.transport.requests

from app.models.purchase_model import Purchase

ANDROID_PUBLISHER_SCOPE = "https://www.googleapis.com/auth/androidpublisher"
TOKEN_URL_TEMPLATE = (
    "https://androidpublisher.googleapis.com/androidpublisher/v3/"
    "applications/{packageName}/purchases/products/{productId}/tokens/{token}"
)

class GooglePlayService:
    def __init__(self, service_account_file: str):
        self.service_account_file = service_account_file

    def _get_access_token(self) -> str:
        credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=[ANDROID_PUBLISHER_SCOPE],
        )
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token

    def get_purchase_info(
        self,
        package_name: str,
        product_id: str,
        purchase_token: str,
    ) -> dict:
        access_token = self._get_access_token()
        url = TOKEN_URL_TEMPLATE.format(
            packageName=package_name,
            productId=product_id,
            token=purchase_token,
        )
        headers = {"Authorization": f"Bearer {access_token}"}
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200:
            # 구글 응답 그대로 로깅할 수 있도록 raise 전에 detail 포함
            raise RuntimeError(f"Google verify failed: {res.status_code} {res.text}")
        return res.json()

    def verify_and_persist(
        self,
        session: Session,
        *,
        package_name: str,
        product_id: str,
        purchase_token: str,
        user_id: Optional[int] = None,
    ) -> Purchase:
        # 중복 토큰 방지 (이미 처리된 결제면 그대로 반환)
        existing = session.exec(
            select(Purchase).where(Purchase.purchase_token == purchase_token)
        ).first()
        if existing:
            return existing

        info = self.get_purchase_info(package_name, product_id, purchase_token)

        purchase_state = info.get("purchaseState")           # 0=구매완료
        consumption_state = info.get("consumptionState")
        acknowledged = info.get("acknowledged")
        order_id = info.get("orderId")
        pt_ms = info.get("purchaseTimeMillis")

        purchase_time = None
        if pt_ms:
            # ms → datetime
            purchase_time = datetime.fromtimestamp(int(pt_ms) / 1000.0, tz=timezone.utc)

        # 구매완료(0)만 저장/성공 처리
        if purchase_state != 0:
            # 필요하면 상태코드 1/2 등 다른 케이스에 맞춰 에러 메시지 조절
            raise RuntimeError(f"purchaseState != 0 (state={purchase_state})")

        p = Purchase(
            user_id=user_id,
            package_name=package_name,
            product_id=product_id,
            purchase_token=purchase_token,
            purchase_state=purchase_state,
            consumption_state=consumption_state,
            acknowledged=acknowledged,
            order_id=order_id,
            purchase_time=purchase_time,
            raw_response=json.dumps(info, ensure_ascii=False),
        )
        session.add(p)
        session.commit()
        session.refresh(p)
        return p
