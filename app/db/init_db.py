from sqlmodel import SQLModel, Session
from app.db.session import db_engine
from app.models.user_model import User
from app.schemas.user_schema import UserCreate
from app.services.user_service import UserService

async def create_db_and_tables():
    # DB 리셋 함수, 필요에 따라 주석 해제
    #SQLModel.metadata.drop_all(db_engine)
    # DB 테이블 생성
    SQLModel.metadata.create_all(db_engine)
