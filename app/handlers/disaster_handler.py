from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db_session
from app.models.disaster_model import DisasterInfo 
import app.schemas.disaster_schema


router = APIRouter()

@router.get("/disasters", response_model=app.schemas.disaster_schema.DisasterSummaryResponse)
def get_disasters(sido: str, sigungu: Optional[str] = None, eupmyeon: Optional[str] = None, session: Session = Depends(get_db_session)):
    region_query = sido
    if sigungu:
        region_query += f" {sigungu}"
    if eupmyeon:
        region_query += f" {eupmyeon}"

    disasters = session.query(DisasterInfo).filter(DisasterInfo.active == True).all()

    summary = {}
    for d in disasters:
        summary[d.disaster_type] = summary.get(d.disaster_type, 0) + 1

    return {
        "message": "Get active disasters summary successfully",
        "data": [{"summary": summary, "disasters": disasters}]
    }

@router.get("/disasters/{disaster_id}", response_model=app.schemas.disaster_schema.DisasterDetailResponse)
def get_disaster_detail(disaster_id: int, session: Session = Depends(get_db_session)):
    disaster = session.get(DisasterInfo, disaster_id)
    if not disaster:
        raise HTTPException(status_code=404, detail="Disaster not found")
    return {"message": "DisasterInfo fetched successfully", "data": disaster}
