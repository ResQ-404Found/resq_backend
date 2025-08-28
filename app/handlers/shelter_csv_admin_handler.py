from fastapi import APIRouter, Query, HTTPException
from typing import List
from sqlmodel import Session, select

from app.schemas.shelter_csv_schema import ShelterCSVResponse
from app.services.shelter_csv_service import (
    get_by_priority_from_csv,
    get_nearby_from_csv, ADMIN_CSV,
    get_shelter_by_id_from_csv,
    search_by_name_from_csv,
)

router = APIRouter(prefix="/shelters/csv/admin", tags=["Shelter - CSV - ADMIN"])

@router.get("/nearby", response_model=List[ShelterCSVResponse])
def get_nearby_shelters_admin(
    limit: int = Query(20, ge=1, le=500),
):
    # 위/경도 없이 priority 순 정렬
    return get_by_priority_from_csv(ADMIN_CSV, limit)

@router.get("/search", response_model=List[ShelterCSVResponse])
def search_shelters_admin(
    q: str = Query(..., min_length=1, description="시설명 부분검색어"),
    limit: int = Query(20, ge=1, le=500),
    sort_mode: str = Query(
        "priority",
        regex="^(priority|priority_grade|name|distance|accuracy)$",
        description="정렬 방식 (priority | priority_grade | name | distance | accuracy)"
    ),
):
    return search_by_name_from_csv(
        path=ADMIN_CSV,
        query=q,
        limit=limit,
        sort_mode=sort_mode,
    )

@router.get("/{shelter_id}", response_model=ShelterCSVResponse)
def get_shelter_detail_admin(
    shelter_id: str,
):
    row = get_shelter_by_id_from_csv(ADMIN_CSV, shelter_id)
    if not row:
        raise HTTPException(status_code=404, detail="Shelter not found")
    return row
