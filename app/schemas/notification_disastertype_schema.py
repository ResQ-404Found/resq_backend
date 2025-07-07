from pydantic import BaseModel

class NotificationDisasterTypeCreate(BaseModel):
    disaster_type: str

class NotificationDisasterTypeRead(BaseModel):
    id: int
    user_id: int
    disaster_type: str

    class Config:
        orm_mode = True
