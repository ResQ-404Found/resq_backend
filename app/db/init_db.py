from sqlmodel import SQLModel, Session
from app.db.session import db_engine
from app.models.user_model import User
from app.schemas.user_schema import UserCreate
from app.services.user_service import UserService

async def create_db_and_tables():
    SQLModel.metadata.drop_all(db_engine)
    SQLModel.metadata.create_all(db_engine)

    # 테스트 유저 생성
    with Session(db_engine) as session:
        test_user1 = UserCreate(
            login_id="test1",
            email="test1@gmail.com",
            password="test1",
            username="test1",
        )
        test_user2 = UserCreate(
            login_id="test2",
            email="test2@gmail.com",
            password="test2",
            username="test2",
        )
        user_service = UserService(session)
        user_service._save(test_user1)
        user_service._save(test_user2)
