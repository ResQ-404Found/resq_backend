from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_db_session
from app.handlers.user_handler import get_current_user
from app.models.user_model import User
from app.schemas.notification_disastertype_schema import NotificationDisasterTypeCreate, NotificationDisasterTypeRead
from app.services.notification_disastertype_service import (
    create_notification_disastertype,
    get_notification_disastertypes_by_user,
    delete_notification_disastertype
)

router = APIRouter()

@router.post("/notification-disastertypes", response_model=NotificationDisasterTypeRead)
def create_disastertype(req: NotificationDisasterTypeCreate, user: User = Depends(get_current_user), session: Session = Depends(get_db_session)):
    return create_notification_disastertype(session, user.id, req.disaster_type)

@router.get("/notification-disastertypes", response_model=list[NotificationDisasterTypeRead])
def get_user_disastertypes(user: User = Depends(get_current_user), session: Session = Depends(get_db_session)):
    return get_notification_disastertypes_by_user(session, user.id)

@router.delete("/notification-disastertypes/{disastertype_id}")
def delete_disastertype(disastertype_id: int, user: User = Depends(get_current_user), session: Session = Depends(get_db_session)):
    success = delete_notification_disastertype(session, disastertype_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="NotificationDisasterType not found")
    return {"message": "Deleted successfully"}
