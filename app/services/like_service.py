from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.session import get_db_session
from app.models import PostLike, CommentLike, Post, Comment

class LikeService:
    def __init__(self, db: Session=Depends(get_db_session)):
        self.db = db
    
    # 게시물 좋아요 토글 (좋아요 추가/취소)
    def toggle_post_like(self, post_id: int, user_id: int) -> int:
        post = self.db.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시물이 존재하지 않습니다.")
        
        existing_like = self.db.exec(
            select(PostLike).where(
                PostLike.post_id == post_id,
                PostLike.user_id == user_id
            )
        ).first()
        
        if existing_like:
            self.db.delete(existing_like)
            post.like_count = max(0, post.like_count - 1)
        else:
            new_like = PostLike(post_id=post_id, user_id=user_id)
            self.db.add(new_like)
            post.like_count += 1
        self.db.commit()
        self.db.refresh(post)
        return post.like_count
    
    # 댓글 좋아요 토글 (좋아요 추가/취소)
    def toggle_comment_like(self, comment_id: int, user_id: int) -> int:
        comment = self.db.get(Comment, comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="댓글이 존재하지 않습니다.")    
        
        existing_like = self.db.exec(
            select(CommentLike).where(
                CommentLike.comment_id == comment_id,
                CommentLike.user_id == user_id
            )
        ).first()
        
        if existing_like:
            self.db.delete(existing_like)
            comment.like_count = max(0, comment.like_count - 1)
        else:
            new_like = CommentLike(comment_id=comment_id, user_id=user_id)
            self.db.add(new_like)
            comment.like_count += 1
        self.db.commit()
        self.db.refresh(comment)
        return comment.like_count
    
    # 게시물 좋아요 상태 확인
    def get_post_like_status(self, post_id: int, user_id: int) -> bool:
        post = self.db.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시물이 존재하지 않습니다.")
        
        like = self.db.exec(
            select(PostLike).where(
                PostLike.post_id == post_id,
                PostLike.user_id == user_id
            )
        ).first()
        return like is not None
    
    # 댓글 좋아요 상태 확인
    def get_comment_like_status(self, comment_id: int, user_id: int) -> bool:
        comment = self.db.get(Comment, comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="댓글이 존재하지 않습니다.")
        
        like = self.db.exec(
            select(CommentLike).where(
                CommentLike.comment_id == comment_id,
                CommentLike.user_id == user_id
            )
        ).first()
        return like is not None 