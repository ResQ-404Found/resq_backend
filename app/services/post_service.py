from datetime import datetime
from typing import List, Optional
from fastapi.concurrency import run_in_threadpool
from sqlmodel import Session, select
from fastapi import HTTPException, UploadFile

from app.models.post_model import Post
from app.schemas.post_schemas import PostCreate, PostUpdate
from app.utils.s3_util import delete_file_from_s3, upload_file_to_s3

class PostService:
    def __init__(self, session: Session):
        self.session = session

    async def create_post(
        self, 
        post_data: PostCreate, 
        user_id: int, 
        files: Optional[List[UploadFile]] = None
    ) -> Post:
        image_urls = []
        if files:
            for file in files:
                file_bytes = await file.read()
                image_url = await run_in_threadpool(upload_file_to_s3, file_bytes, file.filename, "uploads/post")
                image_urls.append(image_url)
        post_data.post_imageURLs = image_urls

        post = Post(
            **post_data.dict(),
            user_id=user_id
        )
        self.session.add(post)
        self.session.commit()
        self.session.refresh(post)
        return post

    def get_post(self, post_id: int, raise_exception: bool = True) -> Post:
        post = self.session.get(Post, post_id)
        if not post and raise_exception:
            raise HTTPException(status_code=404, detail="Post not found")
        return post

    async def update_post(
        self,
        post_id: int,
        post_data: PostUpdate,
        current_user_id: int,
        files: Optional[List[UploadFile]] = None
    ) -> Post:
        post = self.get_post(post_id)
        if post.user_id != current_user_id:
            raise HTTPException(status_code=403, detail="작성자만 수정할 수 있습니다.")
        
        existing_urls = set(post.post_imageURLs or [])
        requested_urls = set(post_data.post_imageURLs or [])
        if files:
            for file in files:
                file_bytes = await file.read()
                image_url = await run_in_threadpool(upload_file_to_s3, file_bytes, file.filename, "uploads/post")
                requested_urls.add(image_url)
        
        urls_to_delete = existing_urls - requested_urls
        for url in urls_to_delete:
            delete_file_from_s3(url)
        post_data.post_imageURLs = list(requested_urls)

        for key, value in post_data.dict(exclude_none=True).items():
            setattr(post, key, value)
        self.session.add(post)
        self.session.commit()
        self.session.refresh(post)
        return post

    def delete_post(self, post_id: int, current_user_id: int):
        post = self.get_post(post_id)
        if post.user_id != current_user_id:
            raise HTTPException(status_code=403, detail="작성자만 삭제할 수 있습니다.")
        
        if post.post_imageURLs:
            for url in post.post_imageURLs:
                delete_file_from_s3(url)
        self.session.delete(post)
        self.session.commit()
        return {"ok": True}

    def list_posts(self, term: str = None, region_ids: list = None, sort: str = None):
        query = select(Post)

        if term:
            query = query.where(Post.title.contains(term) | Post.content.contains(term))

        if region_ids:
            query = query.where(Post.region_id.in_(region_ids))

        if sort == "latest":
            query = query.order_by(Post.created_at.desc())
        elif sort == "popular":
            query = query.order_by(Post.view_count.desc())

        return self.session.exec(query).all()

    def list_user_posts(self, user_id: int):
        return self.session.exec(select(Post).where(Post.user_id == user_id)).all()

    def increment_view_count(self, post_id: int):
        post = self.get_post(post_id)
        post.view_count += 1
        self.session.add(post)
        self.session.commit()
        self.session.refresh(post)
        return post
