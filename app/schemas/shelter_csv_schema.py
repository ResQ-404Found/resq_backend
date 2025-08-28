from pydantic import BaseModel
from typing import Optional

class ShelterCSVResponse(BaseModel):
    source: Optional[str]
    HCODE: Optional[int]
    SIGUNGU: Optional[str]
    EUPMYEON: Optional[str]
    name: str
    address: Optional[str]
    type_name: Optional[str]
    type_code: Optional[int]
    assigned_pop: Optional[float]
    capacity_est: Optional[float]
    p_elderly: Optional[float]
    p_child: Optional[float]
    vuln: Optional[float]
    recommend_score: Optional[float]
    lat: float
    lon: float
    distance_km: Optional[float] = None  # 사용자 입력 좌표 기준 거리
