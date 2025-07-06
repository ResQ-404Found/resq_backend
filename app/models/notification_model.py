from datetime import datetime
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel

class NotificationDisasterType(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    disaster_type: str

    user: Optional["User"] = Relationship(back_populates="notification_disastertypes")

class NotificationRegion(SQLModel,table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    region_id: int = Field(foreign_key="region.id", nullable=False)

    user: Optional["User"] = Relationship(back_populates="notification_regions")
    region: Optional["Region"] = Relationship(back_populates="notification_regions")

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    disaster_id: int = Field(foreign_key="disasterinfo.id", nullable=False)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    title: str
    body: str
    is_sent: bool = Field(default=False)
    send_at: Optional[datetime] = Field(default=None)

    user: Optional["User"] = Relationship(back_populates="notifications")
    disaster: Optional["DisasterInfo"] = Relationship(back_populates="notifications")