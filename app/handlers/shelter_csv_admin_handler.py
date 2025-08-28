from fastapi import APIRouter, Query, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from sqlmodel import Session, select

from app.schemas.shelter_csv_schema import ShelterCSVResponse
from app.services.shelter_csv_service import get_nearby_from_csv, ADMIN_CSV, get_shelter_by_id_from_csv
from app.db.session import db_engine
from app.models.user_model import User, UserRole
from app.utils.jwt_util import JWTUtil, resolve_role_from_token_or_db  # ← 여기 사용

router = APIRouter(prefix="/shelters/csv/admin", tags=["Shelter - CSV - ADMIN"])

bearer = HTTPBearer(auto_error=False)  # 토큰 없으면 None

def require_admin_user(creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer)) -> User:
    # 1) 비로그인
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required")

    token = creds.credentials

    # 2) payload 디코드 (jwt_util의 SECRET/ALGORITHM과 동일하게)
    try:
        payload = JWTUtil.decode_token(token)  # 여기서 만료/유효성 예외 처리됨
    except HTTPException as e:
        # 메시지는 jwt_util 그대로 사용
        raise e

    # 3) role 확인 (payload.role 우선, 없으면 DB로 복원)
    role = resolve_role_from_token_or_db(token)
    if role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")

    # 4) sub로 실제 사용자 조회
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    try:
        uid = int(sub)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    with Session(db_engine) as session:
        user = session.exec(select(User).where(User.id == uid)).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        if user.role != UserRole.ADMIN:
            # 토큰 role이 ADMIN인데 실제 DB가 USER인 경우도 방지
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
        return user

@router.get("/nearby", response_model=List[ShelterCSVResponse])
def get_nearby_shelters_admin(
    latitude: float = Query(...),
    longitude: float = Query(...),
    limit: int = Query(20, ge=1, le=500),
    _: User = Depends(require_admin_user),
):
    return get_nearby_from_csv(ADMIN_CSV, latitude, longitude, limit)

@router.get("/{shelter_id}", response_model=ShelterCSVResponse)
def get_shelter_detail_admin(
    shelter_id: str,
    _: User = Depends(require_admin_user),
):
    row = get_shelter_by_id_from_csv(ADMIN_CSV, shelter_id)
    if not row:
        raise HTTPException(status_code=404, detail="Shelter not found")
    return row
