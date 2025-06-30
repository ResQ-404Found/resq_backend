from fastapi import APIRouter, Depends
from app.services.like_service import LikeService
from app.schemas.like_schemas import LikeCount, LikeCountResponse, LikeStatus, LikeStatusResponse
from app.handlers.user_handler import get_current_user
from app.models import User

router = APIRouter()

# 게시물 좋아요 누르기
@router.post("/posts/{post_id}/like")
def add_post_like(
    post_id: int,
    current_user: User = Depends(get_current_user),
    like_service: LikeService = Depends()
) -> LikeCountResponse:
    count = like_service.toggle_post_like(post_id, current_user.id)
    return LikeCountResponse(message="게시물 좋아요 추가 성공", data=LikeCount(like_count=count))

# 게시물 좋아요 취소
@router.delete("/posts/{post_id}/like")
def remove_post_like(
    post_id: int,
    current_user: User = Depends(get_current_user),
    like_service: LikeService = Depends()
) -> LikeCountResponse:
    count = like_service.toggle_post_like(post_id, current_user.id)
    return LikeCountResponse(message="게시물 좋아요 취소 성공", data=LikeCount(like_count=count))

# 댓글 좋아요 누르기
@router.post("/comments/{comment_id}/like")
def add_comment_like(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    like_service: LikeService = Depends()
) -> LikeCountResponse:
    count = like_service.toggle_comment_like(comment_id, current_user.id)
    return LikeCountResponse(message="댓글 좋아요 추가 성공", data=LikeCount(like_count=count))

# 댓글 좋아요 취소
@router.delete("/comments/{comment_id}/like")
def remove_comment_like(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    like_service: LikeService = Depends()
) -> LikeCountResponse:
    count = like_service.toggle_comment_like(comment_id, current_user.id)
    return LikeCountResponse(message="댓글 좋아요 취소 성공", data=LikeCount(like_count=count))

# 게시물 좋아요 상태 조회
@router.get("/posts/{post_id}/like/status")
def get_post_like_status(
    post_id: int,
    current_user: User = Depends(get_current_user),
    like_service: LikeService = Depends()
) -> LikeStatusResponse:
    like_status = like_service.get_post_like_status(post_id, current_user.id)
    return LikeStatusResponse(message="게시물 좋아요 상태 조회 성공", data=LikeStatus(liked=like_status))

# 댓글 좋아요 상태 조회
@router.get("/comments/{comment_id}/like/status")
def get_comment_like_status(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    like_service: LikeService = Depends()
) -> LikeStatusResponse:
    like_status = like_service.get_comment_like_status(comment_id, current_user.id)
    return LikeStatusResponse(message="댓글 좋아요 상태 조회 성공", data=LikeStatus(liked=like_status))
