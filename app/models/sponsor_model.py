from datetime import date
from typing import Optional
from sqlmodel import Field, SQLModel

class Sponsor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    disaster_type: str
    title: str
    content: Optional[str] = None
    sponsor_name: str
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    target_money: int = Field(default=0)
    current_money: int = Field(default=0)
    image_url: Optional[str] = None