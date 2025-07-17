
from datetime import date
from typing import Optional
from pydantic import BaseModel


class SponsorCreate(BaseModel):
    disaster_type: str
    title: str
    content: Optional[str] = None
    sponsor_name: str
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    target_money: int

class SponsorUpdate(BaseModel):
    disaster_type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    sponsor_name: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    target_money: Optional[int] = None
    image_url: Optional[str] = None

class SponsorRead(BaseModel):
    id: int
    title: str
    sponsor_name: str
    disaster_type: str
    content: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    target_money: int
    current_money: int
    image_url: Optional[str] = None