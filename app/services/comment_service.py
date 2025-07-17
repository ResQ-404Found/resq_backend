# services/comment_service.py
from sqlmodel import Session, desc, select
from fastapi import HTTPException
from datetime import datetime
from collections import defaultdict

from app.models.comment_models import Comment
from app.models.post_model import Post
from app.schemas.comment_schemas import CommentCreate

# 댓글 생성
def create_comment(session: Session, user_id: int, req: CommentCreate) -> Comment:
    post = session.get(Post, req.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="게시글이 존재하지 않습니다.")
    if req.parent_comment_id is not None:
        parent = session.get(Comment, req.parent_comment_id)
        if not parent:
            raise HTTPException(status_code=404, detail="부모 댓글이 존재하지 않습니다.")
        if parent.parent_comment_id:
            raise HTTPException(status_code=400, detail="대대댓글은 허용되지 않습니다.")
    
    comment = Comment(
        post_id=req.post_id,
        user_id=user_id,
        parent_comment_id=req.parent_comment_id,
        content=req.content,
        last_modified=datetime.utcnow()
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment

# 댓글 조회
def get_comments_by_post(session: Session, post_id: int):
    all_comments = session.exec(
        select(Comment).where(Comment.post_id == post_id)
    ).all()
    
    reply_map = defaultdict(list)
    for c in all_comments:
        if c.parent_comment_id:
            reply_map[c.parent_comment_id].append(c)
    
    root_comments = []
    for c in all_comments:
        if c.parent_comment_id is None:
            c.replies = reply_map.get(c.id, [])
            root_comments.append(c)
    return root_comments

# 댓글 수정
def update_comment(session: Session, comment_id: int, new_content: str, user_id: int):
    comment = session.get(Comment, comment_id)
    if not comment or comment.user_id != user_id:
        raise HTTPException(status_code=403, detail="수정 권한 없음")
    if comment.is_deleted:
        raise HTTPException(status_code=400, detail="삭제된 댓글은 수정할 수 없습니다.")
    
    comment.content = new_content
    comment.last_modified = datetime.utcnow()
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment

# 댓글 삭제
def delete_comment(session: Session, comment_id: int, user_id: int):
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="댓글이 존재하지 않습니다.")
    if comment.user_id != user_id:
        raise HTTPException(status_code=403, detail="삭제 권한 없음")
    if comment.is_deleted:
        raise HTTPException(status_code=400, detail="이미 삭제된 댓글입니다.")
    comment.is_deleted = True
    comment.content = "삭제된 댓글입니다."
    comment.last_modified = datetime.utcnow()
    session.add(comment)
    session.commit()
    return {"message": "댓글 삭제 완료"}

def get_comments_by_user(session: Session, user_id: int):
    return session.exec(select(Comment)
                        .where(Comment.user_id == user_id, Comment.is_deleted == False)
                        .order_by(desc(Comment.last_modified))).all()

