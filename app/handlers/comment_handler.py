from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from app.db.session import get_db_session
from app.models.comment_models import Comment
from app.schemas.comment_schemas import CommentCreate, CommentRead, CommentUpdate
from app.handlers.user_handler import get_current_user

router = APIRouter()

# 댓글 작성하기
@router.post("/", response_model=CommentRead)
def write_comment(comment_data: CommentCreate, session: Session = Depends(get_db_session), user=Depends(get_current_user)):
    comment = Comment(
        post_id=comment_data.post_id,
        content=comment_data.content,
        user_id=user.id,
        created_at=datetime.utcnow(),
        like_count=0
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment

# 특정 게시물에 달린 댓글 조회
@router.get("/post/{post_id}", response_model=List[CommentRead])
def read_comments(post_id: int, session: Session = Depends(get_db_session)):
    comments = session.exec(select(Comment).where(Comment.post_id == post_id)).all()
    return comments

# 댓글 수정하기
@router.put("/{comment_id}", response_model=CommentRead)
def modify_comment(comment_id: int, update_data: CommentUpdate, session: Session = Depends(get_db_session), user=Depends(get_current_user)):
    comment = session.get(Comment, comment_id)
    if not comment or comment.user_id != user.id:
        raise HTTPException(status_code=403, detail="수정 권한 없음")

    comment.content = update_data.content
    comment.last_modified = datetime.utcnow()
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment

# 댓글 삭제하기
@router.delete("/{comment_id}")
def remove_comment(comment_id: int, session: Session = Depends(get_db_session), user=Depends(get_current_user)):
    comment = session.get(Comment, comment_id)
    if not comment or comment.user_id != user.id:
        raise HTTPException(status_code=403, detail="삭제 권한 없음")

    session.delete(comment)
    session.commit()
    return {"message": "댓글 삭제 완료"}

# 내가 쓴 댓글 조회
@router.get("/me", response_model=List[CommentRead])
def get_my_comments(session: Session = Depends(get_db_session), user=Depends(get_current_user)):
    return session.exec(select(Comment).where(Comment.user_id == user.id)).all()
