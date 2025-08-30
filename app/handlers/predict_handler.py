from fastapi import APIRouter
from app.schemas.predict_schema import PredictRequest, PredictResponse
from app.services.predict_service import predict_damage

router = APIRouter(prefix="/predict", tags=["Prediction"])

@router.post("", response_model=PredictResponse)
def predict(req: PredictRequest):
    return predict_damage(req.region, req.use_yesterday)
