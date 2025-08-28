from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from sqlmodel import Session, select

from app.schemas.shelter_csv_schema import ShelterCSVResponse
from app.services.shelter_csv_service import (
    get_by_priority_from_csv,  # ← 추가
    get_nearby_from_csv, ADMIN_CSV, get_shelter_by_id_from_csv
)
from app.db.session import db_engine
from app.models.user_model import User, UserRole
from app.utils.jwt_util import JWTUtil, resolve_role_from_token_or_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/shelters/csv/admin", tags=["Shelter - CSV - ADMIN"])
bearer = HTTPBearer(auto_error=False)

def require_admin_user(creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer)) -> User:
    if creds is None:
        raise HTTPException(status_code=401, detail="Login required")
    token = creds.credentials
    payload = JWTUtil.decode_token(token)  # 유효성/만료 체크
    role = resolve_role_from_token_or_db(token)
    if role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin only")

    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    try:
        uid = int(sub)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token subject")

    with Session(db_engine) as session:
        user = session.exec(select(User).where(User.id == uid)).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        if user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Admin only")
        return user

@router.get("/nearby", response_model=List[ShelterCSVResponse])
def get_nearby_shelters_admin(
    limit: int = Query(20, ge=1, le=500),
    _: User = Depends(require_admin_user),
):
    # 위/경도 없이 priority 순 정렬
    return get_by_priority_from_csv(ADMIN_CSV, limit)

@router.get("/{shelter_id}", response_model=ShelterCSVResponse)
def get_shelter_detail_admin(
    shelter_id: str,
    _: User = Depends(require_admin_user),
):
    row = get_shelter_by_id_from_csv(ADMIN_CSV, shelter_id)
    if not row:
        raise HTTPException(status_code=404, detail="Shelter not found")
    return row
