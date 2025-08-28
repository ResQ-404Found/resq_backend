# app/services/shelter_csv_service.py
import os
import pandas as pd
from math import radians, sin, cos, asin, sqrt
from typing import List
from app.schemas.shelter_csv_schema import ShelterCSVResponse

# .env에서 경로 읽기 (없으면 data/ 하위 기본값)
USER_CSV = os.getenv("SHELTER_USER_ALL_CSV", "./data/shelters_rank_user_all.csv")
ADMIN_CSV = os.getenv("SHELTER_ADMIN_ALL_CSV", "./data/shelters_rank_admin_all.csv")

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2.0)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2.0)**2
    c = 2.0 * asin(sqrt(a))
    return R * c

def _load_csv(path: str) -> pd.DataFrame:
    # 필요하면 인코딩 후보 추가 가능
    return pd.read_csv(path)

def get_nearby_from_csv(path: str, lat: float, lon: float, limit: int = 20) -> List[ShelterCSVResponse]:
    df = _load_csv(path)

    # 필수 좌표 컬럼 체크
    if "lat" not in df.columns or "lon" not in df.columns:
        raise ValueError(f"CSV '{path}'에 lat/lon 컬럼이 없습니다.")

    # 거리 계산
    df["distance_km"] = df.apply(
        lambda r: _haversine_km(lat, lon, float(r["lat"]), float(r["lon"])),
        axis=1
    )

    # 가까운 순 정렬 → head(limit)
    if limit is not None:
        df = df.sort_values("distance_km", ascending=True).head(limit)
    else:
        df = df.sort_values("distance_km", ascending=True)

    # Pydantic 모델로 변환
    return [ShelterCSVResponse(**row._asdict() if hasattr(row, "_asdict") else row.to_dict())
            for _, row in df.iterrows()]
