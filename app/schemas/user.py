from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    login_id: str
    email: EmailStr
    password: str
    username: str
    profile_imageURL: str | None = None