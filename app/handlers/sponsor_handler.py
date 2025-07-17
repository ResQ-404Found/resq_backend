from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.handlers.user_handler import get_current_user
from app.models.user_model import User
from app.schemas.sponsor_schema import SponsorCreate, SponsorRead, SponsorUpdate
from app.services.sponsor_service import SponsorService


router = APIRouter()

@router.post("/sponsor", response_model=SponsorRead)
async def create_sponsor(
    disaster_type: str = Form(...),
    title: str = Form(...),
    content: Optional[str] = Form(None),
    sponsor_name: str = Form(...),
    start_date: Optional[date] = Form(None),
    due_date: Optional[date] = Form(None),
    target_money: int = Form(...),
    file: Optional[UploadFile] = File(None),
    sponsor_service: SponsorService = Depends()
):
    req = SponsorCreate(
        disaster_type=disaster_type,
        title=title,
        content=content,
        sponsor_name=sponsor_name,
        start_date=start_date,
        due_date=due_date,
        target_money=target_money
    )
    return await sponsor_service.create_sponsor(req, file)

@router.get("/sponsor/{sponsor_id}", response_model=SponsorRead)
def get_sponsor(
    sponsor_id: int,
    sponsor_service: SponsorService = Depends()
):
    return sponsor_service.get_sponsor(sponsor_id)

@router.get("/sponsor", response_model=List[SponsorRead])
def get_all_sponsors(
    sponsor_service: SponsorService = Depends()
):
    return sponsor_service.get_all_sponsors()

@router.patch("/sponsor/{sponsor_id}", response_model=SponsorRead)
async def update_sponsor(
    sponsor_id: int,
    title: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    sponsor_name: Optional[str] = Form(None),
    start_date: Optional[date] = Form(None),
    due_date: Optional[date] = Form(None),
    target_money: Optional[int] = Form(None),
    disaster_type: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    sponsor_service: SponsorService = Depends()
):
    req = SponsorUpdate(
        title=title,
        content=content,
        sponsor_name=sponsor_name,
        start_date=start_date,
        due_date=due_date,
        target_money=target_money,
        disaster_type=disaster_type
    )
    return await sponsor_service.update_sponsor(sponsor_id, req, file)

@router.delete("/sponsor/{sponsor_id}")
def delete_sponsor(
    sponsor_id: int,
    sponsor_service: SponsorService = Depends()
):
    sponsor_service.delete_sponsor(sponsor_id)
    return {"message": "후원자가 삭제되었습니다."}

@router.post("/sponsor/{sponsor_id}/donate", response_model=SponsorRead)
def donate_to_sponsor(
    sponsor_id: int,
    amount: int,
    sponsor_service: SponsorService = Depends(),
    user: User = Depends(get_current_user)
):
    return sponsor_service.donate_to_sponsor(sponsor_id, amount, user)