from sqlmodel import SQLModel, Session
from app.db.session import db_engine
from app.models.user_model import User
from app.schemas.user_schema import UserCreate
from app.services.user_service import UserService
from sqlalchemy import text
# from app.services.user_service import pwd_context 

async def create_db_and_tables():
    # DB 리셋 함수, 필요에 따라 주석 해제
    with db_engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        SQLModel.metadata.drop_all(bind=conn)
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))

    # DB 테이블 생성
    SQLModel.metadata.create_all(db_engine)


    # # 3. 테스트 유저 삽입
    # with Session(db_engine) as session:
    #     dummy_user = User(
    #         login_id="test",
    #         email="test@example.com",
    #         password=pwd_context.hash("test"),
    #         username="관리자",
    #         role="admin",
    #         profile_imageURL=None,
    #         status="active"
    #     )
    #     session.add(dummy_user)
    #     session.commit()