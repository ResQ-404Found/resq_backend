from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_db_session
from app.schemas.user_schema import UserCreate, UserCreateResponse
from app.services.user_service import UserService
from app.core.redis import get_redis
from redis.asyncio import Redis
from app.utils.redis_util import is_email_verified, clear_email_verified

router = APIRouter()

@router.post("/users/signup")
async def create_user(
    req:UserCreate, 
    db: Session = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
    user_service:UserService=Depends()
) -> UserCreateResponse:
    if not await is_email_verified(redis, req.email):
        raise HTTPException(status_code=400, detail="이메일 인증을 먼저 완료하세요.")
    token_pair = user_service.register(req)
    
    await clear_email_verified(redis, req.email)
    return UserCreateResponse(message="회원가입 성공", data=token_pair)