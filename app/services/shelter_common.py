# app/routers/shelter_common.py
from math import radians, cos, sin, asin, sqrt
from typing import Dict, Any
from app.schemas.shelter_schemas import ShelterResponse

def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2.0)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2.0)**2
    c = 2.0 * asin(sqrt(a))
    return round(R * c, 4)

def make_row_with_rank(s, rank: Dict[str, Any] | None, distance_km: float) -> Dict[str, Any]:
    base = {
        **ShelterResponse.from_orm(s).model_dump(),
        "distance_km": distance_km,
    }
    if rank:
        base.update({
            "source":          rank.get("source"),
            "HCODE":           rank.get("HCODE"),
            "SIGUNGU":         rank.get("SIGUNGU"),
            "EUPMYEON":        rank.get("EUPMYEON"),
            "priority":        rank.get("priority"),
            "grade_admin":     rank.get("grade_admin") or None,
            "recommend_score": rank.get("recommend_score"),
            "grade_user":      rank.get("grade_user") or None,
            "pressure":        rank.get("pressure"),
            "assigned_pop":    rank.get("assigned_pop"),
            "capacity_est":    rank.get("capacity_est"),
            "p_elderly":       rank.get("p_elderly"),
            "p_child":         rank.get("p_child"),
            "vuln":            rank.get("vuln"),
        })
    return base

def admin_only(row: Dict[str, Any]) -> Dict[str, Any]:
    keep = {
        "id","facility_name","road_address","latitude","longitude",
        "shelter_type_code","shelter_type_name","management_serial_number",
        "distance_km","source","HCODE","SIGUNGU","EUPMYEON",
        "priority","grade_admin","pressure","assigned_pop","capacity_est","p_elderly","p_child","vuln",
    }
    return {k: row.get(k) for k in keep}

def user_only(row: Dict[str, Any]) -> Dict[str, Any]:
    keep = {
        "id","facility_name","road_address","latitude","longitude",
        "shelter_type_code","shelter_type_name","management_serial_number",
        "distance_km","source","HCODE","SIGUNGU","EUPMYEON",
        "recommend_score","grade_user",
    }
    return {k: row.get(k) for k in keep}
