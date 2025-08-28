from pydantic import BaseModel
from typing import Optional

class ShelterCSVResponse(BaseModel):
    id: Optional[int] = None
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
    recommend_score: Optional[float]
    latitude: float
    longitude: float
    distance_km: Optional[float] = None  # 사용자 입력 좌표 기준 거리
