from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_db_session
from app.schemas.notification_region_schema import NotificationRegionCreate, NotificationRegionRead
from app.services.notification_region_service import (
    create_notification_region,
    get_notification_regions_by_user,
    delete_notification_region
)
from app.handlers.user_handler import get_current_user
from app.models.user_model import User

router = APIRouter(prefix="/notification-regions")

@router.post("/", response_model=NotificationRegionRead)
def create_region_subscription(
    req: NotificationRegionCreate,
    session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user)
):
    return create_notification_region(session, user_id=user.id, region_id=req.region_id)

@router.get("/", response_model=list[NotificationRegionRead])
def get_my_regions(
    session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user)
):
    return get_notification_regions_by_user(session, user.id)

@router.delete("/{notification_region_id}")
def delete_region_subscription(
    notification_region_id: int,
    session: Session = Depends(get_db_session),
    user: User = Depends(get_current_user)
):
    success = delete_notification_region(session, notification_region_id, user_id=user.id)
    if not success:
        raise HTTPException(status_code=404, detail="NotificationRegion not found or unauthorized")
    return {"message": "Deleted successfully"}
