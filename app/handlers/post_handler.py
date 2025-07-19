from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlmodel import Session, select
from typing import List, Optional

from app.models.region_model import Region
from app.db.session import get_db_session
from app.models.user_model import User
from app.handlers.user_handler import get_current_user
from app.schemas.post_schemas import PostCreate, PostUpdate, PostRead
from app.services.post_service import PostService

router = APIRouter()

@router.post("/posts", response_model=PostRead)
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    region_id: int = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    
    post_data = PostCreate(
        title=title,
        content=content,
        region_id=region_id,
    )
    service = PostService(session)
    return await service.create_post(post_data, current_user, files)

@router.get("/posts", response_model=List[PostRead])
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

@router.get("/posts/me", response_model=List[PostRead])
def read_my_posts(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    service = PostService(session)
    return service.list_user_posts(current_user)

@router.get("/posts/{post_id}", response_model=PostRead)
def read_post(post_id: int, session: Session = Depends(get_db_session)):
    service = PostService(session)
    return service.increment_view_count(post_id)

@router.patch("/posts/{post_id}", response_model=PostRead)
async def update_post(
    post_id: int,
    title: Optional[str] = Form(None),  
    content: Optional[str] = Form(None),
    region_id: Optional[int] = Form(None),
    post_imageURLs: Optional[List[str]] = Form(None),
    files: Optional[List[UploadFile]] = File(None),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    post_data = PostUpdate(
        title=title or None,
        content=content or None,
        region_id=region_id,
        post_imageURLs = [url for url in post_imageURLs or [] if url] or None
    )
    service = PostService(session)
    return await service.update_post(post_id, post_data, current_user, files)

@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    service = PostService(session)
    return service.delete_post(post_id, current_user)
