# app/routers/shelter_user_router.py
from fastapi import APIRouter, Depends, Query, Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session as SA_Session
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from app.db.session import get_db_session
from app.models.shelter_models import Shelter
from app.services.shelter_rank_service import lookup_by_latlon
from app.services.shelter_common import make_row_with_rank, user_only
from sqlmodel import Session as SM_Session, select  

router = APIRouter(prefix="/shelters", tags=["Shelter - USER"])
bearer = HTTPBearer(auto_error=False)

@router.get("/nearby/user", response_model=dict)
def get_nearby_shelters_user(
    latitude: float = Query(...),
    longitude: float = Query(...),
    limit: int = Query(20, ge=1, le=500),
    sort: str = Query("distance", pattern="^(distance|recommend)$"),
    db: SA_Session = Depends(get_db_session),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer),
):
    """
    빠른 경로:
      - sort=distance: DB가 직접 거리 계산 + LIMIT
      - sort=recommend: DB가 먼저 근처 K개만 추려서 파이썬에서 recommend_score 정렬
    """
    # 1) DB에서 근처 우선 추출
    # 위도 1km ≈ 0.009도, 경도 보정 cos(lat)
    from math import cos, radians
    RADIUS_KM_FOR_CANDIDATES = 50.0  # 추천 정렬일 때 후보 폭을 넉넉히
    dlat = RADIUS_KM_FOR_CANDIDATES * 0.009
    dlon = RADIUS_KM_FOR_CANDIDATES * 0.009 * cos(radians(latitude))

    if sort == "distance":
        # DB가 직접 거리 계산 + 정렬 + LIMIT → 최속
        sql = text("""
            SELECT
              id, facility_name, road_address, latitude, longitude,
              shelter_type_code, shelter_type_name, management_serial_number,
              (6371 * 2 * ASIN(SQRT(
                 POWER(SIN(RADIANS(:lat - latitude)/2), 2) +
                 COS(RADIANS(:lat)) * COS(RADIANS(latitude)) *
                 POWER(SIN(RADIANS(:lon - longitude)/2), 2)
              ))) AS distance_km
            FROM shelter
            WHERE latitude BETWEEN :lat_min AND :lat_max
              AND longitude BETWEEN :lon_min AND :lon_max
            ORDER BY distance_km ASC
            LIMIT :limit
        """)
        raw = db.execute(sql, {
            "lat": latitude, "lon": longitude,
            "lat_min": latitude - dlat, "lat_max": latitude + dlat,
            "lon_min": longitude - dlon, "lon_max": longitude + dlon,
            "limit": limit,
        }).mappings().all()

        rows: List[Dict[str, Any]] = []
        for r in raw:
            # CSV 랭킹 붙이기 (근접/정확 매칭)
            rank = lookup_by_latlon(r["latitude"], r["longitude"]) or {}
            # make_row_with_rank는 distance_km 계산을 안 하므로 r값 사용
            base = {
                "id": r["id"],
                "facility_name": r["facility_name"],
                "road_address": r["road_address"],
                "latitude": r["latitude"],
                "longitude": r["longitude"],
                "shelter_type_code": r["shelter_type_code"],
                "shelter_type_name": r["shelter_type_name"],
                "management_serial_number": r["management_serial_number"],
            }
            row = base | {
                "distance_km": float(r["distance_km"]) if r["distance_km"] is not None else None
            }
            # 랭킹 메타 합치기
            row.update({
                "source":          rank.get("source"),
                "HCODE":           rank.get("HCODE"),
                "SIGUNGU":         rank.get("SIGUNGU"),
                "EUPMYEON":        rank.get("EUPMYEON"),
                "priority":        rank.get("priority"),
                "grade_admin":     rank.get("grade_admin") or None,
                "recommend_score": rank.get("recommend_score"),
                "grade_user":      rank.get("grade_user") or None,
            })
            rows.append(row)

        data = [user_only(r) for r in rows]
        return {
            "message": "Nearby shelters (USER view)",
            "data": data,
            "meta": {
                "sorted_by": "distance_km(asc)",
                "input": {"latitude": latitude, "longitude": longitude, "limit": limit, "sort": sort},
            },
        }

    # sort == "recommend": 후보를 DB에서 먼저 모아서 CSV 점수로 정렬
    # 후보 K는 limit보다 크게 (예: 5배) → 추천 점수 반영 여지 확보
    K = min(5 * limit, 500)  # 상한 500
    sql = text("""
        SELECT
          id, facility_name, road_address, latitude, longitude,
          shelter_type_code, shelter_type_name, management_serial_number,
          (6371 * 2 * ASIN(SQRT(
             POWER(SIN(RADIANS(:lat - latitude)/2), 2) +
             COS(RADIANS(:lat)) * COS(RADIANS(latitude)) *
             POWER(SIN(RADIANS(:lon - longitude)/2), 2)
          ))) AS distance_km
        FROM shelter
        WHERE latitude BETWEEN :lat_min AND :lat_max
          AND longitude BETWEEN :lon_min AND :lon_max
        ORDER BY distance_km ASC
        LIMIT :limit
    """)
    raw = db.execute(sql, {
        "lat": latitude, "lon": longitude,
        "lat_min": latitude - dlat, "lat_max": latitude + dlat,
        "lon_min": longitude - dlon, "lon_max": longitude + dlon,
        "limit": K,
    }).mappings().all()

    rows: List[Dict[str, Any]] = []
    for r in raw:
        rank = lookup_by_latlon(r["latitude"], r["longitude"]) or {}
        row = {
            "id": r["id"],
            "facility_name": r["facility_name"],
            "road_address": r["road_address"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "shelter_type_code": r["shelter_type_code"],
            "shelter_type_name": r["shelter_type_name"],
            "management_serial_number": r["management_serial_number"],
            "distance_km": float(r["distance_km"]) if r["distance_km"] is not None else None,
            "source":          rank.get("source"),
            "HCODE":           rank.get("HCODE"),
            "SIGUNGU":         rank.get("SIGUNGU"),
            "EUPMYEON":        rank.get("EUPMYEON"),
            "priority":        rank.get("priority"),
            "grade_admin":     rank.get("grade_admin") or None,
            "recommend_score": rank.get("recommend_score"),
            "grade_user":      rank.get("grade_user") or None,
        }
        rows.append(row)

    # 추천 점수로 정렬 (없으면 뒤)
    rows.sort(key=lambda r: (0, -float(r["recommend_score"])) if r.get("recommend_score") is not None else (1, 0.0))
    rows = rows[:limit]

    data = [user_only(r) for r in rows]
    return {
        "message": "Nearby shelters (USER view)",
        "data": data,
        "meta": {
            "sorted_by": "recommend_score(desc) with DB pre-limit",
            "input": {"latitude": latitude, "longitude": longitude, "limit": limit, "sort": sort},
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
