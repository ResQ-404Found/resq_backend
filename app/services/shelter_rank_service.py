# app/services/shelter_rank_service.py
import os, math, threading
import pandas as pd

USER_ALL_CSV  = os.getenv("SHELTER_USER_ALL_CSV",  "/content/shelters_rank_user_all.csv")
ADMIN_ALL_CSV = os.getenv("SHELTER_ADMIN_ALL_CSV", "/content/shelters_rank_admin_all.csv")
MATCH_RADIUS_M = float(os.getenv("SHELTER_NEARBY_MATCH_RADIUS_M", "600"))


_LOCK = threading.Lock()
_LOADED = False
_IDX = {}          # (round(lat,5), round(lon,5)) -> dict(row)
_ALL_ROWS = []     # 근접 탐색용 전체 행(dict) 리스트
_ALL_LATLON = []   # [(lat, lon), ...] 근접 탐색용

def _safe_read_csv(path: str) -> pd.DataFrame | None:
    if not path or not os.path.exists(path):
        return None
    for enc in ("utf-8", "utf-8-sig", "cp949", "euc-kr"):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            pass
    return None

def _grade_user(v):
    try:
        v = float(v)
    except: 
        return "NA"
    if not math.isfinite(v) or v <= 0: return "NA"
    if v < 0.5: return "D"
    if v < 1.0: return "C"
    if v < 1.5: return "B"
    return "A"

def _grade_admin(v):
    try:
        v = float(v)
    except:
        return "NA"
    if not math.isfinite(v): return "NA"
    if v < 50: return "D"
    if v < 200: return "C"
    if v < 500: return "B"
    return "A"

def _norm_num(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except:
        return None

def _row_to_payload(row: pd.Series) -> dict:
    return {
        "id":              row.get("id"),
        "source":          row.get("source"),
        "HCODE":           row.get("HCODE"),
        "SIGUNGU":         row.get("SIGUNGU"),
        "EUPMYEON":        row.get("EUPMYEON"),
        "facility_name":   row.get("name") or row.get("REARE_NM") or row.get("MGC_NM"),
        "road_address":    row.get("address"),
        "shelter_type_name": row.get("type_name"),
        "shelter_type_code": row.get("type_code"),
        "assigned_pop":    _norm_num(row.get("assigned_pop")),
        "capacity_est":    _norm_num(row.get("capacity_est")),
        "p_elderly":       _norm_num(row.get("p_elderly")),
        "p_child":         _norm_num(row.get("p_child")),
        "vuln":            _norm_num(row.get("vuln")),
        "pressure":        _norm_num(row.get("pressure")),
        "recommend_score": _norm_num(row.get("recommend_score")),
        "priority":        _norm_num(row.get("priority")),
        "latitude":        _norm_num(row.get("lat")),
        "longitude":       _norm_num(row.get("lon")),
    }


def _prep(df: pd.DataFrame, is_user: bool):
    if df is None or df.empty: 
        return pd.DataFrame()
    df = df.copy()
    if "name" not in df.columns:
        for c in ("REARE_NM","MGC_NM"):
            if c in df.columns: 
                df["name"] = df[c]; break
    keep = {
        "source","HCODE","SIGUNGU","EUPMYEON","name","address","type_name","type_code",
        "assigned_pop","capacity_est","p_elderly","p_child","vuln","pressure",
        "recommend_score","priority","lat","lon"
    }
    df = df[[c for c in df.columns if c in keep]]
    if is_user and "recommend_score" not in df.columns:
        df["recommend_score"] = None
    if (not is_user) and "priority" not in df.columns:
        df["priority"] = None
    return df

def _merge_user_admin(user_df: pd.DataFrame | None, admin_df: pd.DataFrame | None) -> pd.DataFrame:
    U = _prep(user_df, True)
    A = _prep(admin_df, False)
    if U.empty and A.empty: 
        return pd.DataFrame()
    if U.empty:
        A["recommend_score"] = None
        return A
    if A.empty:
        U["priority"] = None
        return U
    # 좌표가 다를 수 있으므로 단순 outer concat 후 중복 제거(동일 lat/lon은 사용자 우선)
    merged = pd.concat([U.assign(_src="U"), A.assign(_src="A")], ignore_index=True)
    # 같은 좌표가 둘 다 있으면 사용자(U) 우선으로 정리
    merged.sort_values(by=["lat","lon","_src"], ascending=[True,True,True], inplace=True)
    merged = merged.drop_duplicates(subset=["lat","lon"], keep="first")
    return merged.drop(columns=["_src"], errors="ignore")

def _build_index(df: pd.DataFrame):
    global _IDX, _ALL_ROWS, _ALL_LATLON
    _IDX = {}
    _ALL_ROWS = []
    _ALL_LATLON = []

    for _, row in df.iterrows():
        lat = _norm_num(row.get("lat")); lon = _norm_num(row.get("lon"))
        if lat is None or lon is None: 
            continue
        payload = _row_to_payload(row)
        key = (round(lat,5), round(lon,5))
        _IDX[key] = payload
        _ALL_ROWS.append(payload)
        _ALL_LATLON.append((lat, lon))

def ensure_loaded():
    global _LOADED
    if _LOADED: 
        return
    with _LOCK:
        if _LOADED: 
            return
        user_df  = _safe_read_csv(USER_ALL_CSV)
        admin_df = _safe_read_csv(ADMIN_ALL_CSV)
        merged = _merge_user_admin(user_df, admin_df)
        print(f"[RANK] user_rows={0 if user_df is None else len(user_df)}, admin_rows={0 if admin_df is None else len(admin_df)}, merged={len(merged)}")
        if not merged.empty:
         print("[RANK] sample columns:", list(merged.columns)[:20])
        if merged is None or merged.empty:
            _LOADED = True
            return
        merged["grade_user"]  = merged["recommend_score"].apply(_grade_user)
        merged["grade_admin"] = merged["priority"].apply(_grade_admin)
        _build_index(merged)
        _LOADED = True

def _haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    from math import radians, sin, cos, asin, sqrt
    dlat = radians(lat2-lat1)
    dlon = radians(lon2-lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2*R*asin(sqrt(a))

def lookup_by_latlon(lat: float, lon: float) -> dict | None:
    ensure_loaded()
    if not _IDX and not _ALL_ROWS:
        return None

    lat = float(lat); lon = float(lon)
    # 1) 점진적 라운딩 키 조회: 5→4→3
    for d in (5, 4, 3):
        key = (round(lat, d), round(lon, d))
        row = _IDX.get(key)
        if row:
            return row


    # 2) 근접 탐색 (env로 조절되는 반경)
    best = None; best_d = 1e18
    for (lt, ln), r in zip(_ALL_LATLON, _ALL_ROWS):
        d = _haversine_m(lat, lon, lt, ln)
        if d < best_d:
            best = r; best_d = d
    if best is not None and best_d <= MATCH_RADIUS_M:
        return best
    return None


def grade_user(score: float | None) -> str:
    return _grade_user(score)

def grade_admin(priority: float | None) -> str:
    return _grade_admin(priority)
