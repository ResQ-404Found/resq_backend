# app/routers/shelter_user_router.py
from fastapi import APIRouter, Depends, Query, Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session as SA_Session
from sqlmodel import Session as SM_Session, select
from typing import Optional, List, Dict, Any

from app.db.session import get_db_session, db_engine
from app.models.shelter_models import Shelter
from app.services.shelter_rank_service import lookup_by_latlon
from app.services.shelter_common import calculate_distance_km, make_row_with_rank, user_only
from app.utils.jwt_util import resolve_role_from_token_or_db

router = APIRouter(prefix="/shelters", tags=["Shelter - USER"])
bearer = HTTPBearer(auto_error=False)

@router.get("/nearby/user", response_model=dict)
def get_nearby_shelters_user(
    latitude: float = Query(...),
    longitude: float = Query(...),
    limit: int = Query(10, ge=1, le=200),
    db: SA_Session = Depends(get_db_session),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer),
):
    # 로그인 여부와 무관하게 접근 허용, 정렬은 USER 기준
    shelters: List[Shelter] = db.query(Shelter).all()
    rows: List[Dict[str, Any]] = []

    for s in shelters:
        if s.latitude is None or s.longitude is None:
            continue
        dist_km = calculate_distance_km(latitude, longitude, s.latitude, s.longitude)
        rank = lookup_by_latlon(s.latitude, s.longitude) or {}
        row = make_row_with_rank(s, rank, dist_km)
        rows.append(row)

    # USER 정렬: recommend_score desc, None은 뒤
    def sort_key(r):
        sc = r.get("recommend_score")
        return (0, -float(sc)) if sc is not None else (1, 0.0)
    rows.sort(key=sort_key)

    data = [user_only(r) for r in rows[:limit]]
    return {
        "message": "Nearby shelters (USER view)",
        "data": data,
        "meta": {
            "sorted_by": "recommend_score(desc)",
            "input": {"latitude": latitude, "longitude": longitude, "limit": limit},
        },
    }

@router.get("/{shelter_id}/user", response_model=dict)
def get_shelter_user(
    shelter_id: int,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer),
):
    with SM_Session(db_engine) as session:
        s = session.exec(select(Shelter).where(Shelter.id == shelter_id)).first()
        if not s:
            raise HTTPException(status_code=404, detail={"error": "Shelter not found"})
        rank = lookup_by_latlon(s.latitude, s.longitude) or {}
        row = make_row_with_rank(s, rank, 0.0)
        return {
            "message": "Shelter fetched (USER view)",
            "data": user_only(row),
        }
