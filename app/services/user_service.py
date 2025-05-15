from sqlmodel import Session
from fastapi import HTTPException, Depends
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, TokenPair
from app.utils.jwt_util import JWTUtil
from passlib.context import CryptContext
from app.db.session import get_db_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: Session=Depends(get_db_session)):
        self.db = db
    
    # 외부에서 호출하는 메서드
    def register(self, req: UserCreate) -> TokenPair:
        self._exception_if_duplicate("login_id", req.login_id)
        self._exception_if_duplicate("email", req.email)
        self._exception_if_duplicate("username", req.username)
        user = self._save(req)
        return JWTUtil.generate_token_pair(user.id)

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
        if (self.db.query(User).filter(getattr(User, field) == value).first() is not None):
            raise HTTPException(400, detail=f"{field}가 이미 존재합니다.")