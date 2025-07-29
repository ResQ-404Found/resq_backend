from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List

from app.db.session import get_db_session
from app.schemas.comment_schemas import CommentCreate, CommentRead, CommentUpdate
from app.handlers.user_handler import get_current_user
from app.services.comment_service import create_comment, delete_comment, get_comments_by_post, get_comments_by_user, update_comment

router = APIRouter()

# 내가 쓴 댓글 조회
@router.get("/comments/me", response_model=List[CommentRead])
def get_my_comments(
    session: Session = Depends(get_db_session), 
    user=Depends(get_current_user)
):
    return get_comments_by_user(session=session, user_id=user.id)

# 댓글 작성하기
@router.post("/comments", response_model=CommentRead)
def write_comment(
    req: CommentCreate,
    session: Session = Depends(get_db_session),
    user=Depends(get_current_user)
):
    return create_comment(session=session, user=user, req=req)

# 특정 게시물에 달린 댓글 조회
@router.get("/comments/{post_id}", response_model=List[CommentRead])
def read_comments(
    post_id: int, 
    session: Session = Depends(get_db_session)
):
    return get_comments_by_post(session=session, post_id=post_id)

# 댓글 수정하기
@router.patch("/comments/{comment_id}", response_model=CommentRead)
def modify_comment(
    comment_id: int, 
    req: CommentUpdate, 
    session: Session = Depends(get_db_session), 
    user=Depends(get_current_user)
):
    return update_comment(session=session, comment_id=comment_id, new_content=req.content, user_id=user.id)

# 댓글 삭제하기
@router.patch("/comments/{comment_id}/delete")
def remove_comment(
    comment_id: int, 
    session: Session = Depends(get_db_session), 
    user=Depends(get_current_user)
):
    return delete_comment(session=session, comment_id=comment_id, user_id=user.id)


