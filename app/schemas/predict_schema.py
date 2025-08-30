from pydantic import BaseModel

class PredictRequest(BaseModel):
    region: str
    use_yesterday: bool = False

class PredictResponse(BaseModel):
    date: str
    region: str
    TA: float        # 기온 (°C)
    RN_DAY: float    # 일강수량 (mm)
    WS: float        # 풍속 (m/s)
    message_exists: bool
    lat: float
    lon: float
    pred_damage: float
    pred_radius_m: float
