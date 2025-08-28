from fastapi import APIRouter, Query
from typing import List
from app.services.shelter_csv_service import get_nearby_from_csv, ADMIN_CSV
from app.schemas.shelter_csv_schema import ShelterCSVResponse

router = APIRouter(prefix="/shelters/csv/admin", tags=["Shelter - CSV - ADMIN"])

@router.get("/nearby", response_model=List[ShelterCSVResponse])
def get_nearby_shelters_admin(
    latitude: float = Query(...),
    longitude: float = Query(...),
    limit: int = Query(20, ge=1, le=500),
):
    return get_nearby_from_csv(ADMIN_CSV, latitude, longitude, limit)
