from http.client import HTTPException
from typing import List, Optional
from fastapi import Depends, UploadFile
from fastapi.concurrency import run_in_threadpool
from sqlmodel import select
from sqlmodel import Session

from app.db.session import get_db_session
from app.models.sponsor_model import Sponsor
from app.models.user_model import User
from app.schemas.sponsor_schema import SponsorCreate, SponsorUpdate
from app.utils.s3_util import delete_file_from_s3, upload_file_to_s3


class SponsorService:
    def __init__(self, session: Session=Depends(get_db_session)):
        self.session = session
    
    async def create_sponsor(self, data: SponsorCreate, file: Optional[UploadFile] = None) -> Sponsor:
        image_url = None
        if file:
            file_bytes = await file.read()
            image_url = await run_in_threadpool(
                upload_file_to_s3, file_bytes, file.filename, "uploads/sponsor"
            )
        sponsor = Sponsor(
            **data.dict(),
            image_url=image_url
        )
        self.session.add(sponsor);
        self.session.commit();
        self.session.refresh(sponsor)
        return sponsor
    
    def get_sponsor(self, sponsor_id: int) -> Sponsor:
        sponsor = self.session.get(Sponsor, sponsor_id)
        if not sponsor:
            raise HTTPException(status_code=404, detail="Sponsor not found");
        return sponsor
    
    def get_all_sponsors(self):
        return self.session.exec(select(Sponsor)).all()
    
    async def update_sponsor(self, sponsor_id: int, data: SponsorUpdate, file: Optional[UploadFile] = None) -> Sponsor:
        sponsor = self.get_sponsor(sponsor_id)
        update_data = data.dict(exclude_unset=True)
        if file:
            if sponsor.image_url:
                delete_file_from_s3(sponsor.image_url)
            file_bytes = await file.read()
            new_image_url = await run_in_threadpool(
                upload_file_to_s3, file_bytes, file.filename, "uploads/sponsor"
            )
            update_data["image_url"] = new_image_url
        for key, value in update_data.items():
            if value is not None:
                setattr(sponsor, key, value)
        self.session.add(sponsor)
        self.session.commit()
        self.session.refresh(sponsor)
        return sponsor
    
    def delete_sponsor(self, sponsor_id: int) -> bool:
        sponsor = self.get_sponsor(sponsor_id)
        if sponsor.image_url:
            delete_file_from_s3(sponsor.image_url)
        self.session.delete(sponsor)
        self.session.commit()
        return True
    
    def donate_to_sponsor(self, sponsor_id: int, amount: int, user: User) -> Sponsor:
        sponsor = self.get_sponsor(sponsor_id)
        sponsor.current_money += amount
        user.point += (amount // 1000) * 100
        self.session.add_all([sponsor, user])
        self.session.commit()
        self.session.refresh(sponsor)
        return sponsor