from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_db_session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.redis import get_redis

example_router = APIRouter()

@example_router.get("/")
def hello():
    return {"message": "Hello FastAPI!"}

@example_router.get("/users")
def db_test(session: Session = Depends(get_db_session)):
    user = session.exec(select(User)).first()
    if user:
        return {"status": "connected", "user": user.username}
    else:
        return {"status": "connected", "message": "no users found"}
    

@example_router.post("/users")
def create_user(user_create: UserCreate, session: Session = Depends(get_db_session)):
    # 중복 확인
    existing = session.exec(select(User).where(User.login_id == user_create.login_id)).first()
    if existing:
        raise HTTPException(status_code=400, detail="login_id already exists")

    # 유저 생성
    user = User(**user_create.dict())
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User created", "user_id": user.id}

@example_router.get("/redis-ping")
async def redis_ping(redis = Depends(get_redis)):
    await redis.set("ping", "pong")
    value = await redis.get("ping")
    return {"result": value}
