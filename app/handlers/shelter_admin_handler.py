# app/routers/shelter_admin_router.py
from fastapi import APIRouter, Depends, Security, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session as SA_Session
from sqlmodel import Session as SM_Session, select
from typing import Optional, List, Dict, Any
from sqlmodel import Session as SM_Session, select  
from app.db.session import get_db_session, db_engine
from app.models.shelter_models import Shelter
from app.services.shelter_rank_service import lookup_by_latlon
from app.services.shelter_common import make_row_with_rank, admin_only
from app.utils.jwt_util import resolve_role_from_token_or_db

router = APIRouter(prefix="/shelters")
bearer = HTTPBearer(auto_error=True)  # ADMIN은 토큰 필수

def _ensure_admin(credentials: HTTPAuthorizationCredentials):
    role = resolve_role_from_token_or_db(credentials.credentials if credentials else None)
    if role != "ADMIN":
        raise HTTPException(status_code=403, detail="ADMIN 권한이 필요합니다.")

@router.get("/nearby/admin", response_model=dict)
def get_all_shelters_admin(
    limit: Optional[int] = Query(None, ge=1, le=500),
    db: SA_Session = Depends(get_db_session),
    credentials: HTTPAuthorizationCredentials = Security(bearer),
):
    _ensure_admin(credentials)

    shelters = db.query(Shelter).all()
    rows = []
    for s in shelters:
        if s.latitude is None or s.longitude is None:
            continue
        rank = lookup_by_latlon(s.latitude, s.longitude) or {}
        row = make_row_with_rank(s, rank, 0.0)
        rows.append(row)

    rows.sort(key=lambda r: (0, -float(r["priority"])) if r.get("priority") is not None else (1, 0.0))
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



@router.get("/{shelter_id}/admin", response_model=dict)
def get_shelter_admin(
    shelter_id: int,
    credentials: HTTPAuthorizationCredentials = Security(bearer),
):
    _ensure_admin(credentials)

    with SM_Session(db_engine) as session:
        s = session.exec(select(Shelter).where(Shelter.id == shelter_id)).first()
        if not s:
            raise HTTPException(status_code=404, detail={"error": "Shelter not found"})
        rank = lookup_by_latlon(s.latitude, s.longitude) or {}
        row = make_row_with_rank(s, rank, 0.0)  # distance 사용 안 함 → 0.0
        return {
            "message": "Shelter fetched (ADMIN view)",
            "data": admin_only(row),
        }
