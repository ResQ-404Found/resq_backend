from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
#from app.models.disasterInfo_model import DisasterInfo

class Region(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sido: str
    sigungu: Optional[str] = None
    eupmyeondong: Optional[str] = None

