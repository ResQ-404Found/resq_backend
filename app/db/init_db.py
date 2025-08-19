from sqlmodel import SQLModel, Session
from app.db.session import db_engine
from app.models.notification_model import NotificationDisasterType, NotificationRegion
from app.models.region_model import Region
from app.models.user_model import User, UserRole
from app.schemas.user_schema import UserCreate
from app.services.user_service import UserService
from sqlalchemy import text
from app.services.user_service import pwd_context 

async def create_db_and_tables():
    # DB 리셋 함수, 필요에 따라 주석 해제
    with db_engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        SQLModel.metadata.drop_all(bind=conn)
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))

    # DB 테이블 생성
    SQLModel.metadata.create_all(db_engine)


    # 3. 테스트 유저 삽입
    with Session(db_engine) as session:
        dummy_user = User(
            login_id="Admin",
            email="resq.404found@gmail.com",
            password=pwd_context.hash("Admin"),
            username="username",
            role=UserRole.ADMIN,
            profile_imageURL=None,
            status="active"
        )
        session.add(dummy_user)
        # ← 새 테스트 유저 추가
        tester = User(
            login_id="test",
            email="tester01@example.com",
            password=pwd_context.hash("test"),
            username="test",       # 닉네임(검색에 사용할 username)
            role=UserRole.ADMIN,
            profile_imageURL=None,
            status="active"
            # fcm_token=None  # 필요 시 세팅
        )
        session.add(tester)
        session.commit()
        session.refresh(dummy_user)

        region = Region(
            sido="경상북도",
            sigungu="의성군",
        )
        session.add(region)
        session.commit()
        session.refresh(region)

        user_id = dummy_user.id
        region_id = region.id
    
    with Session(db_engine) as session:
        notification_region = NotificationRegion(
        user_id=user_id,
        region_id=region_id
        )
        session.add(notification_region)
        session.commit()

        notification_disastertype = NotificationDisasterType(
        user_id=user_id,
        disaster_type="폭염"   # 예시: 원하는 재난 타입
        )
        session.add(notification_disastertype)
        session.commit()
