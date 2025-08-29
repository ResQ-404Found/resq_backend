from pydantic import BaseModel
from typing import Optional

class PredictRequest(BaseModel):
    date: str                # "YYYY-MM-DD"
    region: str              # 지역명
    avgTa: float             # 평균기온
    sumRn: float             # 강수량
    avgWs: float             # 풍속
    message_exists: bool     # 재난문자 존재 여부
    lat: Optional[float] = None  # 위도
    lon: Optional[float] = None  # 경도

class PredictResponse(BaseModel):
    date: str
    region: str
    pred_damage: float       # 예측 피해면적 (헥타르)
    lat: Optional[float] = None
    lon: Optional[float] = None
