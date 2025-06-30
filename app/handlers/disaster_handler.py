from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db_session
from app.models.disaster_model import DisasterInfo
from app.models.region_model import Region
from app.models.disaster_region_model import DisasterRegion
import app.schemas.disaster_schema
from datetime import datetime

router = APIRouter()

# 재난 목록 조회 (지역별, 타입별 필터링 가능)
@router.get("/disasters", response_model=app.schemas.disaster_schema.DisasterSummaryResponse)
def get_disasters(
    sido: Optional[str] = Query(None, description="시도명"),
    sigungu: Optional[str] = Query(None, description="시군구명"),
    eupmyeondong: Optional[str] = Query(None, description="읍면동명"),
    disaster_type: Optional[str] = Query(None, description="재난 타입"),
    active_only: bool = Query(True, description="활성 재난만 조회"),
    session: Session = Depends(get_db_session)
):
    try:
        # 기본 쿼리: 활성 재난만
        query = session.query(DisasterInfo)
        if active_only:
            query = query.filter(DisasterInfo.active == True)
        
        # 재난 타입 필터링
        if disaster_type:
            query = query.filter(DisasterInfo.disaster_type == disaster_type)
        
        # 지역별 필터링
        if sido or sigungu or eupmyeondong:
            region_query = session.query(Region)
            if sido and not sigungu and not eupmyeondong:
                region_query = region_query.filter(Region.sido == sido)
            elif sido and sigungu and not eupmyeondong:
                region_query = region_query.filter(
                    Region.sido == sido,
                    Region.sigungu == sigungu
                )
            elif sido and sigungu and eupmyeondong:
                region_query = region_query.filter(
                    Region.sido == sido,
                    Region.sigungu == sigungu,
                    Region.eupmyeondong == eupmyeondong
                )

            regions = region_query.all()
            if regions:
                region_ids = [region.id for region in regions]
                disaster_ids = session.query(DisasterRegion.disaster_id).filter(
                    DisasterRegion.region_id.in_(region_ids)
                ).all()
                disaster_ids = [d[0] for d in disaster_ids]
                query = query.filter(DisasterInfo.id.in_(disaster_ids))
        
        disasters = query.order_by(DisasterInfo.start_time.desc()).all()
        
        # 요약 정보 생성
        summary = {}
        for disaster in disasters:
            disaster_type = disaster.disaster_type
            summary[disaster_type] = summary.get(disaster_type, 0) + 1
        
        return {
            "message": "재난정보 조회 성공",
            "data": [{"summary": summary, "disasters": disasters}]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"재난 정보 조회 실패: {str(e)}")

# 특정 재난 상세 정보 조회
@router.get("/disasters/{disaster_id}", response_model=app.schemas.disaster_schema.DisasterDetailResponse)
def get_disaster_detail(disaster_id: int, session: Session = Depends(get_db_session)):
    try:
        disaster = session.get(DisasterInfo, disaster_id)
        if not disaster:
            raise HTTPException(status_code=404, detail="재난 정보가 존재하지 않습니다.")
        
        return {
            "message": "재난 상세 정보 조회 성공", 
            "data": disaster
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"재난 상세정보 조회 실패 : {str(e)}")

# 재난 비활성화 (종료 처리)
@router.put("/disasters/{disaster_id}/deactivate")
def deactivate_disaster(disaster_id: int, session: Session = Depends(get_db_session)):
    try:
        disaster = session.get(DisasterInfo, disaster_id)
        if not disaster:
            raise HTTPException(status_code=404, detail="Disaster not found")
        
        disaster.active = False
        disaster.end_time = datetime.utcnow()
        disaster.updated_at = datetime.utcnow()
        session.commit()
        
        return {
            "message": "재난 비활성화 성공",
            "disaster_id": disaster_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"재난 비활성화 실패: {str(e)}")
