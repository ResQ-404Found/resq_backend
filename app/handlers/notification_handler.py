from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db.session import get_db_session
from app.handlers.user_handler import get_current_user
from app.models.user_model import User
from app.schemas.notification_schema import NotificationCreate, NotificationRead
from app.services.notification_service import (
    create_notification,
    get_notifications_by_user
)

router = APIRouter()

@router.post("/notifications", response_model=NotificationRead)
def create(req: NotificationCreate, user: User = Depends(get_current_user), session: Session = Depends(get_db_session)):
    return create_notification(session, user.id, req.disaster_id, req.title, req.body)

@router.get("/notifications", response_model=list[NotificationRead])
def get_user_notifications(user: User = Depends(get_current_user), session: Session = Depends(get_db_session)):
    return get_notifications_by_user(session, user.id)
