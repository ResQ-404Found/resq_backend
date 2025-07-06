from typing import List, Optional,TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

from app.models.disaster_region_model import DisasterRegion

class Region(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sido: str
    sigungu: Optional[str] = None
    eupmyeondong: Optional[str] = None

    disasters: list["DisasterInfo"] = Relationship(
        back_populates="regions", link_model=DisasterRegion
    )
    posts: List["Post"] = Relationship(back_populates="region")
    notification_regions: List["NotificationRegion"] = Relationship(back_populates="region")
