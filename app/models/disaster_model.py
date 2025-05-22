from sqlmodel import SQLModel, Field,Relationship
from typing import Optional
from datetime import datetime
from typing import Optional,List


class DisasterInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    disaster_type: str
    disaster_level: str
    info: str
    active: bool = True
    start_time: datetime
    end_time: Optional[datetime] = None
    updated_at: datetime
    region: str = Field(default="미상", max_length=1000)

