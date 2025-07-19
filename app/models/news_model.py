from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class News(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    origin_url: str
    naver_url: str
    pub_date: datetime
