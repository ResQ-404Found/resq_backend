from sqlmodel import select, Session
from app.models.disaster_model import DisasterInfo
from app.models.notification_model import Notification, NotificationDisasterType, NotificationRegion
from app.models.user_model import User
from datetime import datetime
from app.db.session import db_engine

from sqlmodel import select
from starlette.concurrency import run_in_threadpool

from app.utils.fcm_util import send_fcm_notification

# 알림 보낼 발송자 필터링
def get_subscribed_user_ids(session: Session, disaster: DisasterInfo) -> set[int]:
    try:
        # regions 관계가 로드되었는지 확인
        if not hasattr(disaster, 'regions') or disaster.regions is None:
            print("[ERROR] Disaster regions 관계가 로드되지 않았습니다.")
            return set()
        
        region_ids = [r.id for r in disaster.regions]
        if not region_ids:
            print("[INFO] 현재 알림 설정된 Region이 없습니다.")
            return set()
        
        region_subscribers = session.exec(
            select(NotificationRegion.user_id).where(
                NotificationRegion.region_id.in_(region_ids)
            )
        ).all()
        disaster_type = disaster.disaster_type
        type_subscribers = session.exec(
            select(NotificationDisasterType.user_id).where(
                NotificationDisasterType.disaster_type == disaster_type
            )
        ).all()
        return set(region_subscribers) & set(type_subscribers)
    except Exception as e:
        print(f"[ERROR] get_subscribed_user_ids 실패: {e}")
        return set()

# 알림 생성
def create_notifications(session: Session, user_ids: set[int], disaster: DisasterInfo):
    if not user_ids:
        #print("[INFO] 구독자 없음, 스킵")
        return []
    
    notifs = []
    for user_id in user_ids:
        title=f"[{disaster.disaster_type}] {disaster.disaster_level}"
        body=disaster.info,
        notif = create_notification(session, user_id, disaster.id, title, body)
        notifs.append(notif)
    return notifs

def send_notifications(session: Session, notifs: list[Notification]):
    for notif in notifs:
        user = session.get(User, notif.user_id)
        if not user or not user.fcm_token:
            print(f"[SKIP] 유효하지 않은 유저/토큰 user_id={notif.user_id}")
            continue
    
        run_in_threadpool(
            send_fcm_notification,
            token=user.fcm_token,
            title=notif.title,
            body=notif.body,
        )
        notif.is_sent = True
        notif.send_at = datetime.utcnow()
        session.add(notif)
        session.commit()

def create_notification(session: Session, user_id: int, disaster_id: int, title: str, body: str) -> Notification:
    obj = Notification(
        user_id=user_id,
        disaster_id=disaster_id,
        title=title,
        body=body,
        created_at=datetime.utcnow(),
        is_sent=False
    )
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

def get_notifications_by_user(session: Session, user_id: int):
    statement = select(Notification).where(Notification.user_id == user_id)
    return session.exec(statement).all()
