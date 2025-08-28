from pydantic import BaseModel
from typing import Optional

class ShelterCSVResponse(BaseModel):
    id: int
    source: Optional[str]
    HCODE: Optional[int]
    SIGUNGU: Optional[str]
    EUPMYEON: Optional[str]
    facility_name: str
    road_address: Optional[str]
    shelter_type_name: Optional[str]
    shelter_type_code: Optional[int]
    assigned_pop: Optional[float]
    capacity_est: Optional[float]
    p_elderly: Optional[float]
    p_child: Optional[float]
    vuln: Optional[float]

    # ▼ 숫자 원본들
    recommend_score: Optional[float]          # 이미 있었음
    priority: Optional[float] = None          # ← 추가

    # 좌표/거리
    latitude: Optional[float]
    longitude: Optional[float]
    distance_km: Optional[float] = None

    # ▼ 등급(문자)
    priority_grade: Optional[str] = None      # ADMIN용
    recommend_grade: Optional[str] = None     # USER용
