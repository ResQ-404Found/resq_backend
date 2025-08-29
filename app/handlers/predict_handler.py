from fastapi import APIRouter, HTTPException
from app.schemas.predict_schema import PredictRequest, PredictResponse
from app.services.predict_service import predict_damage

router = APIRouter(prefix="/predict", tags=["Prediction"])

@router.post("/", response_model=PredictResponse)
def predict_endpoint(req: PredictRequest):
    try:
        result = predict_damage(
            date=req.date,
            region=req.region,
            avgTa=req.avgTa,
            sumRn=req.sumRn,
            avgWs=req.avgWs,
            message_exists=req.message_exists,
            lat=req.lat,
            lon=req.lon
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
