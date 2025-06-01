from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional

from app.models.region_model import Region
from app.db.session import get_db_session
from app.models.user_model import User
from app.handlers.user_handler import get_current_user
from app.schemas.post_schemas import PostCreate, PostUpdate, PostRead
from app.services.post_service import PostService

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=PostRead)
def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    service = PostService(session)
    return service.create_post(post_data, current_user.id)

@router.get("/", response_model=List[PostRead])
def read_posts(
    term: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    session: Session = Depends(get_db_session)
):
    region_ids = None
    if region:
        region_ids = session.exec(select(Region.id).where(Region.sido == region)).all()
    service = PostService(session)
    return service.list_posts(term=term, region_ids=region_ids, sort=sort)

@router.get("/me", response_model=List[PostRead])
def read_my_posts(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    service = PostService(session)
    return service.list_user_posts(current_user.id)

@router.get("/{post_id}", response_model=PostRead)
def read_post(post_id: int, session: Session = Depends(get_db_session)):
    service = PostService(session)
    return service.increment_view_count(post_id)

@router.patch("/{post_id}", response_model=PostRead)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    service = PostService(session)
    return service.update_post(post_id, post_data, current_user.id)

@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    service = PostService(session)
    return service.delete_post(post_id, current_user.id)
