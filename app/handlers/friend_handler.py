from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_db_session
from app.handlers.user_handler import get_current_user
from app.schemas.friend_schema import FriendRequestCreate, FriendRequestRead
from app.services.friend_service import FriendService

router = APIRouter(prefix='/friend')

@router.get("/search")
def search(username: str, s: Session = Depends(get_db_session), user=Depends(get_current_user)):
    res = FriendService(s, user.id).search_users(username)
    return [{"id": u.id, "username": u.username, "profile_imageURL": u.profile_imageURL} for u in res]

@router.post("/requests", response_model=FriendRequestRead, status_code=201)
def send_request(payload: FriendRequestCreate, s: Session = Depends(get_db_session), user=Depends(get_current_user)):
    fr = FriendService(s, user.id).send_request(payload.username)
    return fr

@router.get("/requests/incoming", response_model=List[FriendRequestRead])
def incoming(s: Session = Depends(get_db_session), user=Depends(get_current_user)):
    return FriendService(s, user.id).list_incoming_read()

@router.get("/requests/outgoing", response_model=List[FriendRequestRead])
def outgoing(s: Session = Depends(get_db_session), user=Depends(get_current_user)):
    return FriendService(s, user.id).list_outgoing_read()

@router.post("/requests/{request_id}/accept", response_model=FriendRequestRead)
def accept(request_id: int, s: Session = Depends(get_db_session), user=Depends(get_current_user)):
    try:
        return FriendService(s, user.id).accept(request_id)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/requests/{request_id}/reject", response_model=FriendRequestRead)
def reject(request_id: int, s: Session = Depends(get_db_session), user=Depends(get_current_user)):
    try:
        return FriendService(s, user.id).reject(request_id)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/requests/{request_id}/cancel", response_model=FriendRequestRead)
def cancel(request_id: int, s: Session = Depends(get_db_session), user=Depends(get_current_user)):
    try:
        return FriendService(s, user.id).cancel(request_id)
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.get("")
def list_friends(s: Session = Depends(get_db_session), user=Depends(get_current_user)):
    rows = FriendService(s, user.id).list_friends()
    return [{"id": u.id, "username": u.username, "profile_imageURL": u.profile_imageURL} for u in rows]
