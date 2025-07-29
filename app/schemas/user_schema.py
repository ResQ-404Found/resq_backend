from typing import Optional
from pydantic import BaseModel, EmailStr, HttpUrl
from app.models.user_model import User, UserRole
from app.schemas.common_schema import ApiResponse

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str

class FCMTokenUpdate(BaseModel):
    fcm_token: str

class FCMTestRequest(BaseModel):
    title: str
    body: str

class DirectFCMRequest(BaseModel):
    token: str
    title: str
    body: str

class UserCreate(BaseModel):
    login_id: str
    email: EmailStr
    password: str
    username: str

UserCreateResponse = ApiResponse[TokenPair]

class UserLogin(BaseModel):
    login_id: str
    password: str 

UserLoginResponse = ApiResponse[TokenPair]

class PasswordUpdatePair(BaseModel):
    old_password: str
    new_password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[PasswordUpdatePair] = None

UserUpdateResponse = ApiResponse[None]

UserDeleteResponse = ApiResponse[None]

class UserRead(BaseModel):
    email: EmailStr
    username: str
    point: int
    profile_imageURL: Optional[HttpUrl] = None
    role: UserRole

UserReadResponse = ApiResponse[UserRead]

class ResetPassword(BaseModel):
    email: EmailStr
    new_password: str