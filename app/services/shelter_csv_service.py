# app/services/shelter_csv_service.py
import os
import pandas as pd
from math import radians, sin, cos, asin, sqrt
from typing import List, Optional, Dict, Any
from app.schemas.shelter_csv_schema import ShelterCSVResponse
from typing import List, Optional, Dict, Any
import pandas as pd

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

def _assign_row_ids(df: pd.DataFrame) -> pd.DataFrame:
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

def _normalize_coord_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    다양한 좌표 컬럼명을 latitude/longitude로 정규화하고 숫자화.
    좌표 없는 행은 제거.
    """
    df = df.copy()

    lat_candidates = ["latitude", "lat", "LAT", "Y", "위도"]
    lon_candidates = ["longitude", "lon", "LOT", "X", "경도"]

    def first_existing(cands):
        for c in cands:
            if c in df.columns:
                return c
        return None

    lat_col = first_existing(lat_candidates)
    lon_col = first_existing(lon_candidates)

    if not lat_col or not lon_col:
        raise ValueError(
            "CSV에 좌표 컬럼이 없습니다. (허용 후보: "
            "latitude/longitude, lat/lon, LAT/LOT, X/Y, 경도/위도)"
        )

    # 새 표준 컬럼으로 복사
    df["latitude"] = pd.to_numeric(df[lat_col], errors="coerce")
    df["longitude"] = pd.to_numeric(df[lon_col], errors="coerce")

    # 유효 좌표만 남김
    df = df.dropna(subset=["latitude", "longitude"]).copy()
    return df

def _is_nan(x) -> bool:
    try:
        return pd.isna(x)
    except Exception:
        return False

def _str_or_none(x) -> Optional[str]:
    if x is None or _is_nan(x):
        return None
    s = str(x).strip()
    return s if s != "" else None

def _str_or_empty(x) -> str:
    if x is None or _is_nan(x):
        return ""
    return str(x).strip()

def _to_int(x) -> Optional[int]:
    try:
        if _is_nan(x): 
            return None
        return int(float(x))
    except Exception:
        return None

def _row_to_payload(row: pd.Series) -> Dict[str, Any]:
    r = row.to_dict()

    rid = r.get("id")  # 행기반 id

    # 문자열 후보들에서 고르기
    facility_name = _str_or_empty(_pick_first(r, "facility_name", "name", "REARE_NM", "MGC_NM"))
    road_address  = _str_or_none(_pick_first(r, "road_address", "address"))
    shelter_type_name = _str_or_none(_pick_first(r, "shelter_type_name", "type_name"))

    # 코드/숫자 변환
    shelter_type_code = _to_int(_pick_first(r, "shelter_type_code", "type_code"))

    latitude  = _to_float(_pick_first(r, "latitude", "lat", "LAT"))
    longitude = _to_float(_pick_first(r, "longitude", "lon", "LOT"))

    return {
        "id": rid,
        "source": _str_or_none(r.get("source")),
        "HCODE": _to_int(r.get("HCODE")),
        "SIGUNGU": _str_or_none(r.get("SIGUNGU")),
        "EUPMYEON": _str_or_none(r.get("EUPMYEON")),
        "facility_name": facility_name,          # 필수 필드 → 빈문자열 허용
        "road_address": road_address,            # Optional[str]
        "shelter_type_name": shelter_type_name,  # Optional[str]
        "shelter_type_code": shelter_type_code,  # Optional[int]
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
    df = _assign_row_ids(df)          # 행 기반 id 생성
    df = _normalize_coord_columns(df) # 좌표 컬럼 정규화(+숫자화, 결측 제거)

    # 거리 계산
    df["distance_km"] = df.apply(
        lambda r: _haversine_km(lat, lon, float(r["latitude"]), float(r["longitude"])),
        axis=1
    )

    # 가까운 순 정렬 → head(limit)
    df = df.sort_values("distance_km", ascending=True)
    if limit is not None:
        df = df.head(limit)

    results: List[ShelterCSVResponse] = []
    for _, row in df.iterrows():
        payload = _row_to_payload(row)
        payload["distance_km"] = _to_float(row["distance_km"])
        results.append(ShelterCSVResponse(**payload))
    return results

def get_shelter_by_id_from_csv(
    path: str, 
    shelter_id: str, 
    base_lat: Optional[float] = None, 
    base_lon: Optional[float] = None
) -> Optional[ShelterCSVResponse]:
    """
    행 기반 자동 id(1..N)로 상세 조회.
    base_lat/lon이 주어지면 distance_km 계산해서 포함.
    """
    df = _safe_read_csv(path)
    if df is None or df.empty:
        return None

    df = _assign_row_ids(df)

    try:
        target_id = int(str(shelter_id).strip())
    except ValueError:
        return None

    hit = df[df["id"] == target_id]
    if hit.empty:
        return None

    row = hit.iloc[0]
    payload = _row_to_payload(row)

    # 좌표 있고, 기준 좌표도 들어오면 거리 계산
    if base_lat is not None and base_lon is not None:
        lat = _to_float(payload.get("latitude"))
        lon = _to_float(payload.get("longitude"))
        if lat is not None and lon is not None:
            payload["distance_km"] = _haversine_km(base_lat, base_lon, lat, lon)

    return ShelterCSVResponse(**payload)

def get_by_priority_from_csv(path: str, limit: int = 20) -> List[ShelterCSVResponse]:
    """
    ADMIN 전용: 위경도 없이 priority 내림차순으로 상위 limit개 반환.
    - 좌표는 스키마 필수라서 정규화(_normalize_coord_columns)로 숫자화/결측 제거
    - priority 컬럼 후보: ["priority", "PRIORITY", "admin_priority"]
    - 없거나 숫자 변환 실패 시 가장 낮게 취급
    - distance_km는 계산하지 않음(None)
    """
    df = _safe_read_csv(path)
    if df is None or df.empty:
        return []

    # 행 기반 id 부여
    df = _assign_row_ids(df)

    # 좌표 표준화(스키마에 latitude/longitude 필수이므로 없는 행은 제거)
    df = _normalize_coord_columns(df)

    # priority 정규화
    cand = None
    for c in ("priority", "PRIORITY", "admin_priority"):
        if c in df.columns:
            cand = c
            break

    if cand is None:
        # priority가 없으면 전부 동일 우선순위(=0)로 보고 최신 행부터 id 내림차순 정도로 정렬
        df["_priority_norm"] = 0.0
    else:
        df["_priority_norm"] = pd.to_numeric(df[cand], errors="coerce").fillna(float("-inf"))

    # priority 내림차순, 동점이면 id 오름차순
    df = df.sort_values(by=["_priority_norm", "id"], ascending=[False, True])

    if limit is not None:
        df = df.head(limit)

    results: List[ShelterCSVResponse] = []
    for _, row in df.iterrows():
        payload = _row_to_payload(row)
        # ADMIN 리스트에서는 거리 계산 안 함
        payload["distance_km"] = None
        results.append(ShelterCSVResponse(**payload))

    return results
