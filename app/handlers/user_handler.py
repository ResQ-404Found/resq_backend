from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from sqlmodel import Session
from app.db.session import get_db_session
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserCreateResponse, UserDeleteResponse, UserLogin, UserLoginResponse, UserUpdate, UserUpdateResponse
from app.services.user_service import UserService
from app.core.redis import get_redis
from redis.asyncio import Redis
from app.utils.jwt_util import JWTUtil
from app.utils.redis_util import is_email_verified, clear_email_verified

router = APIRouter()

bearer_scheme = HTTPBearer()

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        user_service: UserService = Depends()
) -> User:
    token = credentials.credentials
    payload = JWTUtil.decode_token(token)
    user_id = payload.get("sub")
    user = user_service.get_user_by_id(user_id)
    return user

@router.post("/users/signup")
async def create_user(
    req:UserCreate, 
    redis: Redis = Depends(get_redis),
    user_service:UserService=Depends()
) -> UserCreateResponse:
    if not await is_email_verified(redis, req.email):
        raise HTTPException(status_code=400, detail="이메일 인증을 먼저 완료하세요.")
    token_pair = user_service.register(req)
    
    await clear_email_verified(redis, req.email)
    return UserCreateResponse(message="회원가입 성공", data=token_pair)

@router.post("/users/signin")
def siginin_user(
    req: UserLogin,
    user_service: UserService = Depends(),
) -> UserLoginResponse:
    token_pair = user_service.login(req)
    return UserLoginResponse(message="로그인 성공", data=token_pair)

@router.post("/refresh")
def refresh_token(authorization: str = Header(...)):
    refresh_token = authorization.replace("Bearer ", "")
    user_id = JWTUtil.decode_refresh_token(refresh_token)
    return {
        "access_token": JWTUtil.generate_access_token(user_id)
    }

@router.patch("/users/update", response_model_exclude_none=True)
def update_user(
    req: UserUpdate,
    user: User=Depends(get_current_user),
    user_service: UserService = Depends(),
) -> UserUpdateResponse:
    user_service.update(user.id, req)
    return UserUpdateResponse(message="회원정보 수정 성공")

@router.patch("/users/delete", response_model_exclude_none=True)
def delete_user(
    user: User=Depends(get_current_user), 
    user_service: UserService = Depends()
) -> UserDeleteResponse:
    user_service.deactivate(user.id)
    return UserDeleteResponse(message="회원탈퇴 성공")

