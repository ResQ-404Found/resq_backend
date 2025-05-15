from pydantic import BaseModel, EmailStr
from app.schemas.common_schema import ApiResponse

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str

class UserCreate(BaseModel):
    login_id: str
    email: EmailStr
    password: str
    username: str

UserCreateResponse = ApiResponse[TokenPair]