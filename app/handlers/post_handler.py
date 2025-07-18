from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlmodel import Session, select
from typing import List, Optional

from app.models.region_model import Region
from app.db.session import get_db_session
from app.models.user_model import User
from app.handlers.user_handler import get_current_user
from app.schemas.post_schemas import PostCreate, PostUpdate, PostRead
from app.services.post_service import PostService
from uuid import uuid4
import os

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
    # 1. 파일 저장 및 URL 생성
    image_urls = []
    if files:
        os.makedirs("static/uploads", exist_ok=True)
        for file in files:
            filename = f"{uuid4().hex}_{file.filename}"
            file_path = os.path.join("static/uploads", filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            # 실제 서비스라면 URL 포맷에 맞춰서 변경
            image_urls.append(f"/static/uploads/{filename}")

    # 2. post 생성
    post_data = PostCreate(
        title=title,
        content=content,
        region_id=region_id,
        post_imageURLs=image_urls if image_urls else None
    )
    service = PostService(session)
    post = service.create_post(post_data, current_user.id, image_urls)
    return service.to_read_dto(post)


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
    posts = service.list_posts(term=term, region_ids=region_ids, sort=sort)
    return [service.to_read_dto(post) for post in posts]

@router.get("/posts/me", response_model=List[PostRead])
def read_my_posts(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    service = PostService(session)
    posts = service.list_user_posts(current_user.id)
    return [service.to_read_dto(post) for post in posts]

@router.get("/posts/{post_id}", response_model=PostRead)
def read_post(post_id: int, session: Session = Depends(get_db_session)):
    service = PostService(session)
    post = service.increment_view_count(post_id)
    return service.to_read_dto(post)

@router.patch("/posts/{post_id}", response_model=PostRead)
async def update_post(
    post_id: int,
    title: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    region_id: Optional[int] = Form(None),
    post_imageURLs: Optional[List[UploadFile]] = File(None),  # ← 여기 변경됨
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    # 이미지 저장
    image_urls = []
    if post_imageURLs:
        os.makedirs("static/uploads", exist_ok=True)
        for file in post_imageURLs:
            filename = f"{uuid4().hex}_{file.filename}"
            file_path = os.path.join("static/uploads", filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            image_urls.append(f"/static/uploads/{filename}")

    # 업데이트용 데이터 생성
    post_data = PostUpdate(
        title=title,
        content=content,
        region_id=region_id
    )

    service = PostService(session)
    post = service.update_post(post_id, post_data, current_user.id, new_image_urls=image_urls)
    return service.to_read_dto(post)

@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    service = PostService(session)
    return service.delete_post(post_id, current_user.id)
