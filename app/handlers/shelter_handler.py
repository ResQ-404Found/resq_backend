#app.handlers.shelter_handler.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from math import radians, cos, sin, asin, sqrt

from app.db.session import get_db_session
from app.models.shelter_models import Shelter
from app.schemas.shelter_schemas import ShelterResponse
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from app.models.shelter_models import Shelter
from app.db.session import db_engine

router = APIRouter()

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

@router.get("/shelters/nearby", response_model=dict)
def get_nearby_shelters(
    latitude: float = Query(...),
    longitude: float = Query(...),
    limit: int = Query(10),
    db: Session = Depends(get_db_session)
):
    shelters = db.query(Shelter).all()

    shelters_with_distance = []
    for shelter in shelters:
        if shelter.latitude is None or shelter.longitude is None:
         continue  # 건너뜀

        dist = calculate_distance(latitude, longitude, shelter.latitude, shelter.longitude)
        print(f"{shelter.facility_name} → 거리: {dist}km")
        shelters_with_distance.append((shelter, dist))

    # 무조건 정렬해서 보여줌 (거리조건 없음)
    sorted_shelters = sorted(shelters_with_distance, key=lambda x: x[1])[:limit]

    result = [
        {
            **ShelterResponse.from_orm(s[0]).dict(),
            "distance_km": round(s[1], 6)
        } for s in sorted_shelters
    ]

    return {
        "message": "Nearby shelters fetched successfully",
        "data": result
    }

@router.get("/shelters/{shelter_id}")
def get_shelter(shelter_id: int):
    with Session(db_engine) as session:
        shelter = session.exec(select(Shelter).where(Shelter.id == shelter_id)).first()
        if not shelter:
            raise HTTPException(status_code=404, detail={"error": "Shelter not found"})

        return {
            "message": "Shelter fetched successfully",
            "data": {
                "facility_name": shelter.facility_name,
                "road_address": shelter.road_address,
                "latitude": shelter.latitude,
                "longitude": shelter.longitude,
                "shelter_type_name": shelter.shelter_type_name
            }
        }