from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session
from sqlmodel import select
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

from app.db.session import get_db_session
from app.models.hospital_model import Hospital, HospitalOperatingHour
from app.schemas.hospital_schema import HospitalRead
from app.schemas.hospital_schema import HospitalOperatingHourRead

router = APIRouter()


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    return R * c


@router.get("/hospital/nearby", response_model=dict)
def get_nearby_hospitals(
    latitude: float = Query(...),
    longitude: float = Query(...),
    limit: int = Query(10),
    db: Session = Depends(get_db_session)
):
    hospitals = db.exec(select(Hospital)).all()

    hospitals_with_distance = []
    for hospital in hospitals:
        if hospital.latitude is None or hospital.longitude is None:
            continue

        dist = calculate_distance(latitude, longitude, hospital.latitude, hospital.longitude)
        hospitals_with_distance.append((hospital, dist))

    sorted_hospitals = sorted(hospitals_with_distance, key=lambda x: x[1])[:limit]

    result = []
    for h, dist in sorted_hospitals:
        result.append({
            "id": h.id,
            "facility_name": h.facility_name,
            "road_address": h.road_address,
            "latitude": h.latitude,
            "longitude": h.longitude,
            "phone_number": h.phone_number,
            "distance_km": round(dist, 6)
        })

    return {
        "message": "Nearby hospitals fetched successfully",
        "data": result
    }


@router.get("/hospital/{hospital_id}", response_model=dict)
def get_hospital_detail(
    hospital_id: int = Path(..., ge=1),
    db: Session = Depends(get_db_session)
):
    hospital = db.get(Hospital, hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    # 오늘 요일 계산
    today_eng = datetime.today().strftime("%A")
    korean_day = {
        "Monday": "월요일",
        "Tuesday": "화요일",
        "Wednesday": "수요일",
        "Thursday": "목요일",
        "Friday": "금요일",
        "Saturday": "토요일",
        "Sunday": "일요일",
    }[today_eng]

    today_hour = db.exec(
        select(HospitalOperatingHour)
        .where(HospitalOperatingHour.hospital_id == hospital_id)
        .where(HospitalOperatingHour.day_of_week == korean_day)
    ).first()

    return {
        "message": "Hospital fetched successfully",
        "data": {
            "facility_name": hospital.facility_name,
            "road_address": hospital.road_address,
            "latitude": hospital.latitude,
            "longitude": hospital.longitude,
            "phone_number": hospital.phone_number,
            "today": korean_day,
            "is_closed": today_hour.is_closed if today_hour else True,
            "open_time": today_hour.open_time if today_hour else None,
            "close_time": today_hour.close_time if today_hour else None
        }
    }
