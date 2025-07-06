from sqlmodel import select
from app.models.notification_model import Notification, NotificationDisasterType, NotificationRegion
from app.tasks.fcm_task import send_fcm_notification

def enqueue_notifications(session, disaster):
    region_ids = [r.id for r in disaster.regions]
    if not region_ids:
        print("[ERROR] 연결된 Region 없음")
        return
    
    disaster_type = disaster.disaster_type
    region_subscribers = session.exec(
        select(NotificationRegion.user_id).where(
            NotificationRegion.region_id.in_(region_ids)
        )
    ).all()

    type_subscribers = session.exec(
        select(NotificationDisasterType.user_id).where(
            NotificationDisasterType.disaster_type == disaster_type
        )
    )
    subscribed_user_ids = set(region_subscribers) & set(type_subscribers)
    
    if not subscribed_user_ids:
        return
    subscribed_user_ids = set(subscribed_user_ids)

    for user_id in subscribed_user_ids:
        notifination = Notification(
            user=user_id,
            disaster_id=disaster.id,
            title=f"[{disaster.disaster_type}] {disaster.disaster_level}",
            body=disaster.info,
            is_sent=False
        )
        session.add(notifination)
        session.flush()
        send_fcm_notification.delay(notifination.id)
    print("[INFO] 알림 등록 & 큐 전송 완료")
