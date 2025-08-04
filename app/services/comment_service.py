# services/comment_service.py
from sqlmodel import Session, desc, select
from fastapi import HTTPException
from datetime import datetime
from collections import defaultdict

from app.models.comment_models import Comment
from app.models.post_model import Post
from app.models.user_model import User
from app.schemas.comment_schemas import CommentCreate, CommentRead, Author

# 댓글 생성
def create_comment(session: Session, user: User, req: CommentCreate) -> Comment:
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
        user_id=user.id,
        parent_comment_id=req.parent_comment_id,
        content=req.content,
        last_modified=datetime.utcnow()
    )
    user.point += 2
    session.add(user)
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return _serialize_comment(comment, user)

# 댓글 조회
def get_comments_by_post(session: Session, post_id: int):
    all_comments = session.exec(
        select(Comment).where(Comment.post_id == post_id)
    ).all()

    user_ids = {c.user_id for c in all_comments}
    users = session.exec(select(User).where(User.id.in_(user_ids))).all()
    user_map = {u.id: u for u in users}
    
    reply_map = defaultdict(list)
    comment_map = {}
    for c in all_comments:
        author = user_map.get(c.user_id)
        comment_read = CommentRead(
            id=c.id,
            post_id=c.post_id,
            user_id=c.user_id,
            parent_comment_id=c.parent_comment_id,
            content=c.content,
            created_at=c.created_at,
            last_modified=c.last_modified,
            like_count=c.like_count,
            is_deleted=c.is_deleted,
            author=Author(
                username=author.username,
                profile_imageURL=author.profile_imageURL
            ),
            replies=[]
        )
        comment_map[c.id] = comment_read
        if c.parent_comment_id:
            reply_map[c.parent_comment_id].append(comment_read)

    root_comments = []
    for comment_id, comment in comment_map.items():
        if comment.parent_comment_id is None:
            comment.replies = reply_map.get(comment.id, [])
            root_comments.append(comment)

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
    user = session.get(User, user_id)
    return _serialize_comment(comment, user)

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

# 유저가 작성한 댓글 조회
def get_comments_by_user(session: Session, user_id: int) -> list[CommentRead]:
    comments = session.exec(
        select(Comment)
        .where(Comment.user_id == user_id, Comment.is_deleted == False)
        .order_by(desc(Comment.last_modified))
    ).all()

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자 정보 누락")

    return [
        CommentRead(
            id=c.id,
            post_id=c.post_id,
            user_id=c.user_id,
            parent_comment_id=c.parent_comment_id,
            content=c.content,
            created_at=c.created_at,
            last_modified=c.last_modified,
            like_count=c.like_count,
            is_deleted=c.is_deleted,
            author=Author(
                username=user.username,
                profile_imageURL=user.profile_imageURL
            ),
            replies=[]
        )
        for c in comments
    ]

def _serialize_comment(comment: Comment, user: User) -> CommentRead:
    return CommentRead(
        id=comment.id,
        post_id=comment.post_id,
        user_id=comment.user_id,
        parent_comment_id=comment.parent_comment_id,
        content=comment.content,
        created_at=comment.created_at,
        last_modified=comment.last_modified,
        like_count=comment.like_count,
        is_deleted=comment.is_deleted,
        author=Author(
            username=user.username,
            profile_imageURL=user.profile_imageURL,
        ),
        replies=[],
    )
