from sqlmodel import Session, select
from app.models.notification_model import NotificationDisasterType

def create_notification_disastertype(session: Session, user_id: int, disaster_type: str) -> NotificationDisasterType:
    obj = NotificationDisasterType(user_id=user_id, disaster_type=disaster_type)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

def get_notification_disastertypes_by_user(session: Session, user_id: int) -> list[NotificationDisasterType]:
    statement = select(NotificationDisasterType).where(NotificationDisasterType.user_id == user_id)
    return session.exec(statement).all()

def delete_notification_disastertype(session: Session, disastertype_id: int, user_id: int) -> bool:
    obj = session.get(NotificationDisasterType, disastertype_id)
    if obj and obj.user_id == user_id:
        session.delete(obj)
        session.commit()
        return True
    return False