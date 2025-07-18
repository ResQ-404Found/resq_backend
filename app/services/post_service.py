from datetime import datetime
from sqlmodel import Session, select 
from fastapi import HTTPException 
from sqlalchemy.orm import selectinload
from typing import Optional,List
from app.models.post_model import Post
from app.schemas.post_schemas import PostCreate, PostUpdate, Author,PostRead

class PostService:
    def __init__(self, session: Session):
        self.session = session

    def to_read_dto(self, post: Post) -> PostRead:
        return PostRead(
            id=post.id,
            title=post.title,
            content=post.content,
            created_at=post.created_at,
            view_count=post.view_count,
            like_count=post.like_count,
            post_imageURLs=post.post_imageURLs,  # 여기 추가
            author=Author(
                id=post.user.id,
                nickname=post.user.username,
                profile_image_url=post.user.profile_imageURL
            )
        )

    def create_post(self, post_data: PostCreate, user_id: int, image_urls: list[str] = []) -> Post:
        post = Post(
            **post_data.dict(),
            user_id=user_id,
            post_imageURLs=image_urls  # 이미지 URL 리스트 추가
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
    
    def update_post(self, post_id: int, post_data: PostUpdate, current_user_id: int, new_image_urls: Optional[List[str]] = None) -> Post:
        post = self.get_post(post_id)
        if post.user_id != current_user_id:
            raise HTTPException(status_code=403, detail="작성자만 수정할 수 있습니다.")

        # 일반 필드 업데이트
        for key, value in post_data.dict(exclude_unset=True).items():
            setattr(post, key, value)

        # 이미지 URL 업데이트
        if new_image_urls is not None:
            post.post_imageURLs = new_image_urls

        self.session.add(post)
        self.session.commit()
        self.session.refresh(post)
        return post

    def delete_post(self, post_id: int, current_user_id: int):
        post = self.get_post(post_id)
        if post.user_id != current_user_id:
            raise HTTPException(status_code=403, detail="작성자만 삭제할 수 있습니다.")

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
        query = select(Post).options(selectinload(Post.user)).where(Post.user_id == user_id)
        return self.session.exec(query).all()


    def increment_view_count(self, post_id: int):
        post = self.get_post(post_id)
        post.view_count += 1
        self.session.add(post)
        self.session.commit()
        self.session.refresh(post)
        return post
