# app/services/shelter_csv_service.py
import os
import pandas as pd
from math import radians, sin, cos, asin, sqrt
from typing import List, Optional, Dict, Any
from app.schemas.shelter_csv_schema import ShelterCSVResponse

USER_CSV = os.getenv("SHELTER_USER_ALL_CSV", "./data/shelters_rank_user_all.csv")
ADMIN_CSV = os.getenv("SHELTER_ADMIN_ALL_CSV", "./data/shelters_rank_admin_all.csv")

# ----------------------------
# 내부 유틸
# ----------------------------
def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2.0) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2.0) ** 2
    c = 2.0 * asin(sqrt(a))
    return R * c

def _safe_read_csv(path: str) -> pd.DataFrame:
    last_err: Optional[Exception] = None
    for enc in ("utf-8", "utf-8-sig", "cp949", "euc-kr"):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception as e:
            last_err = e
    raise RuntimeError(f"CSV 읽기 실패: {path} (마지막 오류: {last_err})")

def _ensure_coord_columns(df: pd.DataFrame) -> pd.DataFrame:
    has_latlon = "lat" in df.columns and "lon" in df.columns
    has_latitude = "latitude" in df.columns and "longitude" in df.columns
    if not (has_latlon or has_latitude):
        raise ValueError("CSV에 좌표 컬럼이 없습니다. (필요: (latitude, longitude) 또는 (lat, lon))")
    return df

def _assign_row_ids(df: pd.DataFrame) -> pd.DataFrame:
    """
    원본 CSV의 '행 순서' 기준으로 id 부여 (1부터 시작).
    - reset_index(drop=True)로 고정 인덱스 확보 후 index+1을 id로 사용
    - 이후 정렬/필터링을 해도 id는 컬럼에 유지됨
    """
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    return df

def _to_float(x) -> Optional[float]:
    try:
        v = float(x)
        if v != v:  # NaN
            return None
        return v
    except Exception:
        return None

def _pick_first(d: Dict[str, Any], *keys, default=None):
    for k in keys:
        if k in d and d[k] not in (None, "", "NaN"):
            return d[k]
    return default

def _row_to_payload(row: pd.Series) -> Dict[str, Any]:
    r = row.to_dict()

    # id는 우리가 행기반으로 생성한 값을 그대로 사용
    rid = r.get("id")

    facility_name = _pick_first(r, "facility_name", "name", "REARE_NM", "MGC_NM", default="")
    road_address  = _pick_first(r, "road_address", "address")
    shelter_type_name = _pick_first(r, "shelter_type_name", "type_name")
    shelter_type_code = _pick_first(r, "shelter_type_code", "type_code")

    latitude  = _to_float(_pick_first(r, "latitude", "lat"))
    longitude = _to_float(_pick_first(r, "longitude", "lon"))

    return {
        "id": rid,
        "source": r.get("source"),
        "HCODE": _to_float(r.get("HCODE")),
        "SIGUNGU": r.get("SIGUNGU"),
        "EUPMYEON": r.get("EUPMYEON"),
        "facility_name": facility_name,
        "road_address": road_address,
        "shelter_type_name": shelter_type_name,
        "shelter_type_code": _to_float(shelter_type_code) if shelter_type_code is not None else None,
        "assigned_pop": _to_float(r.get("assigned_pop")),
        "capacity_est": _to_float(r.get("capacity_est")),
        "p_elderly": _to_float(r.get("p_elderly")),
        "p_child": _to_float(r.get("p_child")),
        "vuln": _to_float(r.get("vuln")),
        "recommend_score": _to_float(r.get("recommend_score")),
        "latitude": latitude,
        "longitude": longitude,
        "distance_km": _to_float(r.get("distance_km")),
    }

# ----------------------------
# 공개 함수
# ----------------------------
def get_nearby_from_csv(path: str, lat: float, lon: float, limit: int = 20) -> List[ShelterCSVResponse]:
    df = _safe_read_csv(path)
    df = _ensure_coord_columns(df)
    df = _assign_row_ids(df)  # ← 행 기반 id 생성

    # 거리 계산에 사용할 좌표 컬럼 결정
    if "latitude" in df.columns and "longitude" in df.columns:
        src_lat_col, src_lon_col = "latitude", "longitude"
    else:
        src_lat_col, src_lon_col = "lat", "lon"

    def _dist(row):
        rlat = _to_float(row[src_lat_col])
        rlon = _to_float(row[src_lon_col])
        if rlat is None or rlon is None:
            return float("inf")
        return _haversine_km(lat, lon, rlat, rlon)

    df["distance_km"] = df.apply(_dist, axis=1)

    df = df.sort_values("distance_km", ascending=True)
    if limit is not None:
        df = df.head(limit)

    results: List[ShelterCSVResponse] = []
    for _, row in df.iterrows():
        payload = _row_to_payload(row)
        payload["distance_km"] = _to_float(row["distance_km"])
        results.append(ShelterCSVResponse(**payload))
    return results

def get_shelter_by_id_from_csv(path: str, shelter_id: str) -> Optional[ShelterCSVResponse]:
    """
    행 기반 자동 id(1..N)로 상세 조회.
    - CSV를 다시 로드하고 동일 규칙으로 id 생성 → 해당 id와 일치하는 행 반환
    """
    df = _safe_read_csv(path)
    if df is None or df.empty:
        return None

    df = _assign_row_ids(df)  # 동일 규칙으로 id 부여
    try:
        target_id = int(str(shelter_id).strip())
    except ValueError:
        return None

    hit = df[df["id"] == target_id]
    if hit.empty:
        return None

    return ShelterCSVResponse(**_row_to_payload(hit.iloc[0]))
