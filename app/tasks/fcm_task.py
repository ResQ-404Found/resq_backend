from celery import shared_task
from sqlmodel import Session
from datetime import datetime
from app.db.session import db_engine
from app.models.notification_model import Notification, User
from app.utils.fcm_util import send_fcm

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def send_fcm_notification(self, notification_id: int):
    with Session(db_engine) as session:
        notification = session.get(Notification, notification_id)
        user = session.get(User, notification.user_id)

        if not user or not user.fcm_token:
            return;

        success = send_fcm(
            token=user.fcm_token,
            title=notification.title,
            body=notification.body
        )

        if success:
            notification.is_sent = True
            notification.send_at = datetime.utcnow()