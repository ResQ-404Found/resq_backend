from pydantic import BaseModel, EmailStr

class EmailVerificationRequest(BaseModel):
    email: EmailStr

class EmailVerificationCodeRequest(BaseModel):
    email: EmailStr
    code: str

class PasswordResetCodeRequest(BaseModel):
    email: EmailStr
    code: str