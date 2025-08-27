# app/routers/shelter_admin_router.py
from fastapi import APIRouter, Depends, Security, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session as SA_Session
from sqlmodel import Session as SM_Session, select
from typing import Optional, List, Dict, Any

from app.db.session import get_db_session, db_engine
from app.models.shelter_models import Shelter
from app.services.shelter_rank_service import lookup_by_latlon
from app.services.shelter_common import make_row_with_rank, admin_only
from app.utils.jwt_util import resolve_role_from_token_or_db

router = APIRouter(prefix="/shelters", tags=["Shelter - ADMIN"])
bearer = HTTPBearer(auto_error=True)  # ADMIN은 토큰 필수

def _ensure_admin(credentials: HTTPAuthorizationCredentials):
    role = resolve_role_from_token_or_db(credentials.credentials if credentials else None)
    if role != "ADMIN":
        raise HTTPException(status_code=403, detail="ADMIN 권한이 필요합니다.")

@router.get("/nearby/admin", response_model=dict)
def get_all_shelters_admin(
    limit: Optional[int] = Query(None, ge=1, le=500),  # limit 없으면 None → 전체
    db: SA_Session = Depends(get_db_session),
    credentials: HTTPAuthorizationCredentials = Security(bearer),
):
    _ensure_admin(credentials)

    shelters: List[Shelter] = db.query(Shelter).all()
    rows: List[Dict[str, Any]] = []

    for s in shelters:
        if s.latitude is None or s.longitude is None:
            continue
        rank = lookup_by_latlon(s.latitude, s.longitude) or {}
        row = make_row_with_rank(s, rank, 0.0)  # 거리 제거 → 0.0
        rows.append(row)

    # priority 내림차순 정렬
    def sort_key(r):
        pr = r.get("priority")
        return (0, -float(pr)) if pr is not None else (1, 0.0)
    rows.sort(key=sort_key)

    # limit 적용
    if limit is not None:
        rows = rows[:limit]

    data = [admin_only(r) for r in rows]
    return {
        "message": "Shelters list (ADMIN view)",
        "data": data,
        "meta": {
            "sorted_by": "priority(desc)",
            "count": len(data),
            "limit": limit if limit is not None else "all",
        },
    }
