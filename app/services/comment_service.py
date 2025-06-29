
# services/comment_service.py
from sqlmodel import Session, select
from fastapi import HTTPException
from datetime import datetime

from app.models.comment_models import Comment
from app.schemas.comment_schemas import CommentCreate

def create_comment(session: Session, user_id: int, comment_data: CommentCreate) -> Comment:
    comment = Comment(**comment_data.dict(), user_id=user_id, created_at=datetime.utcnow(), like_count=0)
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment

def get_comments_by_post(session: Session, post_id: int):
    return session.exec(select(Comment).where(Comment.post_id == post_id)).all()

def update_comment(session: Session, comment_id: int, new_content: str, user_id: int):
    comment = session.get(Comment, comment_id)
    if not comment or comment.user_id != user_id:
        raise HTTPException(status_code=403, detail="수정 권한 없음")
    comment.content = new_content
    comment.last_modified = datetime.utcnow()
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment

def delete_comment(session: Session, comment_id: int, user_id: int):
    comment = session.get(Comment, comment_id)
    if not comment or comment.user_id != user_id:
        raise HTTPException(status_code=403, detail="삭제 권한 없음")
    session.delete(comment)
    session.commit()
    return {"msg": "댓글 삭제됨"}

def get_my_comments(session: Session, user_id: int):
    return session.exec(select(Comment).where(Comment.user_id == user_id)).all()

