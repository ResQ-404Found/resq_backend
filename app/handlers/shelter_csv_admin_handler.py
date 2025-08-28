from fastapi import APIRouter, Query, HTTPException
from typing import List
from app.services.shelter_csv_service import get_nearby_from_csv, ADMIN_CSV, get_shelter_by_id_from_csv
from app.schemas.shelter_csv_schema import ShelterCSVResponse

router = APIRouter(prefix="/shelters/csv/admin", tags=["Shelter - CSV - ADMIN"])

@router.get("/nearby", response_model=List[ShelterCSVResponse])
def get_nearby_shelters_admin(
    latitude: float = Query(...),
    longitude: float = Query(...),
    limit: int = Query(20, ge=1, le=500),
):
    return get_nearby_from_csv(ADMIN_CSV, latitude, longitude, limit)

@router.get("/{shelter_id}", response_model=ShelterCSVResponse)
def get_shelter_detail_admin(shelter_id: str):
    row = get_shelter_by_id_from_csv(ADMIN_CSV, shelter_id)
    if not row:
        raise HTTPException(status_code=404, detail="Shelter not found")
    return row
