# app/services/shelter_csv_service.py
import os
from math import radians, sin, cos, asin, sqrt
from typing import List, Optional, Dict, Any, Tuple

import pandas as pd

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

def _to_int(x) -> Optional[int]:
    try:
        if pd.isna(x):
            return None
        return int(float(x))
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

def _row_to_payload(row: pd.Series) -> Dict[str, Any]:
    r = row.to_dict()
    rid = r.get("id")

    facility_name = _str_or_empty(_pick_first(r, "facility_name", "name", "REARE_NM", "MGC_NM"))
    road_address  = _str_or_none(_pick_first(r, "road_address", "address"))
    shelter_type_name = _str_or_none(_pick_first(r, "shelter_type_name", "type_name"))

    shelter_type_code = _to_int(_pick_first(r, "shelter_type_code", "type_code"))

    latitude  = _to_float(_pick_first(r, "latitude", "lat", "LAT"))
    longitude = _to_float(_pick_first(r, "longitude", "lon", "LOT"))

    # ▼ 여기 추가: 다양한 컬럼명에서 priority 수치 뽑기
    priority_val = _to_float(_pick_first(r, "priority", "PRIORITY", "admin_priority"))

    return {
        "id": rid,
        "source": _str_or_none(r.get("source")),
        "HCODE": _to_int(r.get("HCODE")),
        "SIGUNGU": _str_or_none(r.get("SIGUNGU")),
        "EUPMYEON": _str_or_none(r.get("EUPMYEON")),
        "facility_name": facility_name,
        "road_address": road_address,
        "shelter_type_name": shelter_type_name,
        "shelter_type_code": shelter_type_code,
        "assigned_pop": _to_float(r.get("assigned_pop")),
        "capacity_est": _to_float(r.get("capacity_est")),
        "p_elderly": _to_float(r.get("p_elderly")),
        "p_child": _to_float(r.get("p_child")),
        "vuln": _to_float(r.get("vuln")),

        # ▼ 숫자 원본 둘 다 포함
        "recommend_score": _to_float(r.get("recommend_score")),
        "priority": priority_val,

        "latitude": latitude,
        "longitude": longitude,
        "distance_km": _to_float(r.get("distance_km")),
    }

# ----------------------------
# 등급(Grade) 계산 유틸 (분위수 기반)
# ----------------------------
def _quantile_thresholds(series: pd.Series) -> Tuple[float, float, float, float, float]:
    """
    주어진 수치 시리즈에서 (Q25, Q50, Q75, Q90, Q95) 분위수를 반환.
    결측 제거 후 계산. 값이 없으면 전부 0.0 반환.
    """
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return (0.0, 0.0, 0.0, 0.0, 0.0)
    q25 = float(s.quantile(0.25))
    q50 = float(s.quantile(0.50))
    q75 = float(s.quantile(0.75))
    q90 = float(s.quantile(0.90))
    q95 = float(s.quantile(0.95))
    return (q25, q50, q75, q90, q95)

def _grade_by_thresholds(value: Optional[float], q25: float, q50: float, q75: float, q90: float, q95: float) -> Optional[str]:
    """
    값과 분위수 컷오프를 받아 A~F 등급으로 변환.
    """
    if value is None:
        return None
    v = float(value)
    if v >= q95: return "A"
    if v >= q90: return "B"
    if v >= q75: return "C"
    if v >= q50: return "D"
    if v >= q25: return "E"
    return "F"

# ----------------------------
# 공개 함수
# ----------------------------
def get_nearby_from_csv(path: str, lat: float, lon: float, limit: int = 20) -> List[ShelterCSVResponse]:
    """
    USER용: 기준 좌표에서 가까운 순으로 반환 + recommend_grade 계산
    """
    df = _safe_read_csv(path)
    df = _assign_row_ids(df)          # 행 기반 id 생성
    df = _normalize_coord_columns(df) # 좌표 컬럼 정규화(+숫자화, 결측 제거)

    # 거리 계산
    df["distance_km"] = df.apply(
        lambda r: _haversine_km(lat, lon, float(r["latitude"]), float(r["longitude"])),
        axis=1
    )

    # recommend_score 분위수 계산(등급 컷오프)
    q25, q50, q75, q90, q95 = _quantile_thresholds(df.get("recommend_score", pd.Series(dtype=float)))

    # 가까운 순 정렬 → head(limit)
    df = df.sort_values("distance_km", ascending=True)
    if limit is not None:
        df = df.head(limit)

    results: List[ShelterCSVResponse] = []
    for _, row in df.iterrows():
        payload = _row_to_payload(row)
        payload["distance_km"] = _to_float(row["distance_km"])
        # USER: recommend_grade 추가
        payload["recommend_grade"] = _grade_by_thresholds(
            _to_float(row.get("recommend_score")),
            q25, q50, q75, q90, q95
        )
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
    (상세에서는 등급은 선택적; 필요하면 USER/ADMIN 컨텍스트에서 다시 계산 가능)
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
    - distance_km는 계산하지 않음(None)
    - priority_grade(A~F) 포함
    """
    df = _safe_read_csv(path)
    if df is None or df.empty:
        return []

    # 행 기반 id 부여
    df = _assign_row_ids(df)

    # 좌표 표준화(스키마에 latitude/longitude 필수이므로 없는 행은 제거)
    df = _normalize_coord_columns(df)

    # priority 후보 고르기 + 정규화
    cand = None
    for c in ("priority", "PRIORITY", "admin_priority"):
        if c in df.columns:
            cand = c
            break

    if cand is None:
        df["_priority_norm"] = 0.0
        q25 = q50 = q75 = q90 = q95 = 0.0
    else:
        df["_priority_norm"] = pd.to_numeric(df[cand], errors="coerce")
        q25, q50, q75, q90, q95 = _quantile_thresholds(df["_priority_norm"])
        df["_priority_norm"] = df["_priority_norm"].fillna(float("-inf"))

    # priority 내림차순, 동점이면 id 오름차순
    df = df.sort_values(by=["_priority_norm", "id"], ascending=[False, True])

    if limit is not None:
        df = df.head(limit)

    results: List[ShelterCSVResponse] = []
    for _, row in df.iterrows():
        payload = _row_to_payload(row)
        payload["distance_km"] = None
        # ADMIN: priority_grade 추가
        pval = _to_float(row.get(cand)) if cand else None
        payload["priority_grade"] = _grade_by_thresholds(pval, q25, q50, q75, q90, q95)
        results.append(ShelterCSVResponse(**payload))

    return results

def _build_name_series(df: pd.DataFrame) -> pd.Series:
    """
    이름 후보(facility_name, name, REARE_NM, MGC_NM) 중 첫 유효값을 문자열로 반환
    """
    cols = [c for c in ["facility_name", "name", "REARE_NM", "MGC_NM"] if c in df.columns]
    if not cols:
        return pd.Series([""] * len(df), index=df.index, dtype=object)
    s = df[cols[0]].astype("string")
    for c in cols[1:]:
        s = s.fillna(df[c].astype("string"))
    return s.fillna("")

def search_by_name_from_csv(
    path: str,
    query: str,
    limit: int = 20,
    sort_mode: str = "priority",  # "priority" | "name" | "distance" | "priority_grade" | "accuracy"
    base_lat: Optional[float] = None,
    base_lon: Optional[float] = None,
) -> List[ShelterCSVResponse]:
    """
    시설명 부분일치 검색.
    - sort_mode="priority": ADMIN용, priority 내림차순 정렬 (priority_grade 포함)
    - sort_mode="priority_grade": priority_grade 순서(A~F)로 정렬
    - sort_mode="accuracy": 이름 정확도 점수순 정렬
    - sort_mode="name": 이름 사전순 정렬
    - sort_mode="distance": 기준 좌표 있으면 거리순 (recommend_grade 포함)
    """
    df = _safe_read_csv(path)
    if df is None or df.empty:
        return []

    df = _assign_row_ids(df)
    df = _normalize_coord_columns(df)

    # 이름 시리즈
    name_s = _build_name_series(df)
    q = (query or "").strip().lower()
    if not q:
        return []

    mask = name_s.str.lower().str.contains(q, na=False)
    df = df[mask].copy()
    if df.empty:
        return []

    results: List[ShelterCSVResponse] = []

    # -------------------
    # 거리순 (USER 스타일)
    # -------------------
    if sort_mode == "distance" and base_lat is not None and base_lon is not None:
        df["distance_km"] = df.apply(
            lambda r: _haversine_km(base_lat, base_lon, float(r["latitude"]), float(r["longitude"])),
            axis=1
        )
        q25, q50, q75, q90, q95 = _quantile_thresholds(df.get("recommend_score", pd.Series(dtype=float)))
        df = df.sort_values("distance_km", ascending=True).head(limit)

        for _, row in df.iterrows():
            payload = _row_to_payload(row)
            payload["distance_km"] = _to_float(row["distance_km"])
            payload["recommend_grade"] = _grade_by_thresholds(_to_float(row.get("recommend_score")), q25, q50, q75, q90, q95)
            results.append(ShelterCSVResponse(**payload))
        return results

    # -------------------
    # priority 기준 (ADMIN)
    # -------------------
    if sort_mode in ("priority", "priority_grade"):
        cand = None
        for c in ("priority", "PRIORITY", "admin_priority"):
            if c in df.columns:
                cand = c
                break

        if cand is None:
            df["_priority_norm"] = 0.0
            q25 = q50 = q75 = q90 = q95 = 0.0
        else:
            df["_priority_norm"] = pd.to_numeric(df[cand], errors="coerce")
            q25, q50, q75, q90, q95 = _quantile_thresholds(df["_priority_norm"])
            df["_priority_norm"] = df["_priority_norm"].fillna(float("-inf"))

        # priority_grade 미리 계산
        df["priority_grade"] = df[cand].apply(lambda v: _grade_by_thresholds(_to_float(v), q25, q50, q75, q90, q95))

        if sort_mode == "priority":
            df = df.sort_values(by=["_priority_norm", "id"], ascending=[False, True])
        else:  # priority_grade 순 정렬 (A~F)
            grade_order = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, None: 6}
            df["_grade_order"] = df["priority_grade"].map(grade_order)
            df = df.sort_values(by=["_grade_order", "id"], ascending=[True, True])

        df = df.head(limit)

        for _, row in df.iterrows():
            payload = _row_to_payload(row)
            payload["distance_km"] = None
            payload["priority_grade"] = row.get("priority_grade")
            results.append(ShelterCSVResponse(**payload))
        return results

    # -------------------
    # 이름 정확도
    # -------------------
    if sort_mode == "accuracy":
        def score_fn(name: str) -> int:
            n = (name or "").lower()
            if n == q:
                return 3
            if n.startswith(q):
                return 2
            if q in n:
                return 1
            return 0
        df["_acc_score"] = name_s.apply(score_fn)
        df = df.sort_values(by=["_acc_score", "id"], ascending=[False, True]).head(limit)

        for _, row in df.iterrows():
            payload = _row_to_payload(row)
            payload["distance_km"] = None
            results.append(ShelterCSVResponse(**payload))
        return results

    # -------------------
    # 이름 사전순
    # -------------------
    df["_name_key"] = name_s.str.lower()
    df = df.sort_values("_name_key", ascending=True).head(limit)

    for _, row in df.iterrows():
        payload = _row_to_payload(row)
        payload["distance_km"] = None
        results.append(ShelterCSVResponse(**payload))
    return results
