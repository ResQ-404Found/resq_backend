from datetime import datetime
from redis import Redis
from sqlmodel import Session, select
from fastapi import HTTPException, Depends
from app.core.redis import get_redis
from app.models.user_model import User, UserStatus
from app.schemas.user_schema import UserCreate, TokenPair, UserLogin, UserRead, UserUpdate
from app.utils.jwt_util import JWTUtil
from passlib.context import CryptContext
from app.db.session import get_db_session
from app.utils.redis_util import is_email_verified

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: Session=Depends(get_db_session), redis: Redis=Depends(get_redis)):
        self.db = db
        self.redis = redis
    
    # 외부에서 호출하는 메서드
    def register(self, req: UserCreate) -> TokenPair:
        self._exception_if_duplicate("login_id", req.login_id)
        self._exception_if_duplicate("email", req.email)
        self._exception_if_duplicate("username", req.username)
        user = self._save(req)
        return JWTUtil.generate_token_pair(user.id)
    
    def login(self, req: UserLogin) -> TokenPair:
        user = self.db.exec(select(User).where(User.login_id == req.login_id)).first()
        if not user or user.status == UserStatus.INACTIVE:
            raise HTTPException(400, detail="존재하지 않는 사용자입니다.")
        if not self._verify_password(req.password, user.password):
            raise HTTPException(400, detail="비밀번호가 틀립니다.")
        return JWTUtil.generate_token_pair(user.id)
    
    def get_user_by_id(self, user_id: int) -> User:
        user = self.db.exec(select(User).where(User.id == user_id, User.status == UserStatus.ACTIVE)).first()
        if not user:
            raise HTTPException(404, detail="사용자를 찾을 수 없습니다.")
        return user
    
    def update(self, user_id:int, req: UserUpdate):
        user = self.get_user_by_id(user_id)
        # username 변경
        if req.username and req.username != user.username:
            self._exception_if_duplicate("username", req.username)
            user.username = req.username
        
        # 프로필 이미지 변경
        if req.profile_imageURL:
            user.profile_imageURL = req.profile_imageURL
        
        # 비밀번호 변경
        if req.password:
            if not self._verify_password(req.password.old_password, user.password):
                raise HTTPException(400, detail="현재 비밀번호가 틀립니다.")
            user.password = self._hash_password(req.password.new_password)

        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)

    def deactivate(self, user_id:int):
        user = self.get_user_by_id(user_id)
        if user.status == UserStatus.INACTIVE:
            raise HTTPException(400, detail="이미 탈퇴한 사용자입니다.")
        user.status = UserStatus.INACTIVE
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)

    def get_info(self, user_id:int) -> UserRead:
        user = self.get_user_by_id(user_id)
        return UserRead(
            email=user.email,
            username=user.username,
            profile_imageURL=user.profile_imageURL,
            role=user.role
        )

    # 이메일 인증코드 기반 비밀번호 재설정
    async def reset_password_with_email(self, email: str, new_password: str):
        is_verified = await is_email_verified(self.redis, f"reset:{email}")
        
        if not is_verified:
            raise HTTPException(status_code=400, detail="이메일 인증이 완료되지 않았습니다.")
        
        user = self.db.exec(select(User).where(User.email == email, User.status == UserStatus.ACTIVE)).first()
        if not user:
            raise HTTPException(status_code=400, detail="가입되지 않은 이메일입니다.")
        
        user.password = self._hash_password(new_password)
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)

    # 비밀번호 해시화
    def _hash_password(self, pwd: str) -> str:
        return pwd_context.hash(pwd)
    
    # 비밀번호 검증
    def _verify_password(self, pwd: str, hpwd: str) -> bool:
        return pwd_context.verify(pwd, hpwd)
    
    # DB에 User 저장
    def _save(self, req: UserCreate) -> User:
        user = User(
            login_id=req.login_id,
            email=req.email,
            password=self._hash_password(req.password),
            username=req.username,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    # 중복 필드 검사
    def _exception_if_duplicate(self, field: str, value: str):
        if field not in {"login_id", "email", "username"}:
            raise ValueError("중복 검사할 수 없는 필드입니다.")
        if self.db.exec(select(User).where(getattr(User, field) == value, User.status == UserStatus.ACTIVE)).first():
            raise HTTPException(400, detail=f"{field}가 이미 존재합니다.")