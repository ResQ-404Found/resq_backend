from datetime import datetime
from typing import List, Optional
from fastapi.concurrency import run_in_threadpool
from sqlmodel import Session, select
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import selectinload

from app.models.post_model import Post
from app.models.user_model import User
from app.schemas.post_schemas import Author, PostCreate, PostRead, PostUpdate
from app.utils.s3_util import delete_file_from_s3, upload_file_to_s3

class PostService:
    def __init__(self, session: Session):
        self.session = session

    def _serialize_post(self, post: Post, author: Author) -> PostRead:
        return PostRead(
        id=post.id,
        user_id=post.user_id,
        title=post.title,
        content=post.content,
        type=post.type,
        region_id=post.region_id,
        post_imageURLs=post.post_imageURLs,
        created_at=post.created_at,
        view_count=post.view_count,
        like_count=post.like_count,
        author=author,
        comment_count=len(post.comments) 
    )

    async def create_post(
        self, 
        post_data: PostCreate, 
        user: User, 
        files: Optional[List[UploadFile]] = None
    ) -> PostRead:
        image_urls = []
        if files:
            for file in files:
                file_bytes = await file.read()
                image_url = await run_in_threadpool(upload_file_to_s3, file_bytes, file.filename, "uploads/post")
                image_urls.append(image_url)
        post_data.post_imageURLs = image_urls

        post = Post(
            **post_data.dict(),
            user_id=user.id
        )
        if post.type == "disaster":
            user.point += 10
        elif post.type == "normal":
            user.point += 5
        self.session.add(user)
        self.session.add(post)
        self.session.commit()
        self.session.refresh(post)
        author = Author(
            id=user.id,
            username=user.username,
            profile_imageURL=user.profile_imageURL,
            point=user.point
        )
        return self._serialize_post(post, author)

    def get_post(self, post_id: int) -> PostRead:
        post = self.session.exec(
            select(Post).where(Post.id == post_id).options(selectinload(Post.user))).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if post.user is None:
            raise HTTPException(status_code=500, detail="작성자 정보 누락")
        author = Author(
            id=post.user.id,
            username=post.user.username,
            profile_imageURL=post.user.profile_imageURL
            )
        return self._serialize_post(post, author)

    async def update_post(
        self,
        post_id: int,
        post_data: PostUpdate,
        user: User,
        files: Optional[List[UploadFile]] = None
    ) -> Post:
        post = self.session.exec(
            select(Post).where(Post.id == post_id)).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if post.user_id != user.id:
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
        author = Author(
            id=user.id,
            username=user.username,
            profile_imageURL=user.profile_imageURL,
            point=user.point
        )
        return self._serialize_post(post, author)

    def delete_post(self, post_id: int, user: User):
        post = self.session.exec(select(Post).where(Post.id == post_id)).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="작성자만 삭제할 수 있습니다.")
        
        if post.post_imageURLs:
            for url in post.post_imageURLs:
                delete_file_from_s3(url)
        self.session.delete(post)
        self.session.commit()
        return {"ok": True}

    def list_posts(self, term: str = None, type: str = None, region_ids: list = None, sort: str = None):
        query = select(Post).options(selectinload(Post.user))
        if term:
            query = query.where(Post.title.contains(term) | Post.content.contains(term))
        if type:
            query = query.where(Post.type == type)
        if region_ids:
            query = query.where(Post.region_id.in_(region_ids))
        if sort == "latest":
            query = query.order_by(Post.created_at.desc())
        elif sort == "popular":
            query = query.order_by(Post.like_count.desc())
        posts = self.session.exec(query).all()
        return [
        self._serialize_post(
            post,
            Author(
                id=post.user.id,
                username=post.user.username,
                profile_imageURL=post.user.profile_imageURL,
                point=post.user.point
            )
        )
        for post in posts
    ]

    def list_user_posts(self, user: User):
        posts = self.session.exec(select(Post).where(Post.user_id == user.id).options(selectinload(Post.comments))).all()
        author = Author(
            id=user.id,
            username=user.username,
            profile_imageURL=user.profile_imageURL,
            point=user.point
        )
        return [self._serialize_post(post, author) for post in posts]

    def increment_view_count(self, post_id: int):
        post = self.session.exec(
            select(Post).where(Post.id == post_id).options(selectinload(Post.user))
        ).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        post.view_count += 1
        self.session.add(post)
        self.session.commit()
        self.session.refresh(post)
        author = Author(
            id=post.user.id,
            username=post.user.username,
            profile_imageURL=post.user.profile_imageURL,
            point=post.user.point
        )
        return self._serialize_post(post, author)
