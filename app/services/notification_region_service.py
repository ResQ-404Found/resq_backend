from sqlmodel import Session, select
from app.models.notification_model import NotificationRegion

def create_notification_region(session: Session, user_id: int, region_id: int) -> NotificationRegion:
    notification_region = NotificationRegion(user_id=user_id, region_id=region_id)
    session.add(notification_region)
    session.commit()
    session.refresh(notification_region)
    return notification_region

def get_notification_regions_by_user(session: Session, user_id: int) -> list[NotificationRegion]:
    statement = select(NotificationRegion).where(NotificationRegion.user_id == user_id)
    results = session.exec(statement).all()
    return results

def delete_notification_region(session: Session, notification_region_id: int, user_id: int) -> bool:
    obj = session.get(NotificationRegion, notification_region_id)
    if obj and obj.user_id == user_id:
        session.delete(obj)
        session.commit()
        return True
    return False