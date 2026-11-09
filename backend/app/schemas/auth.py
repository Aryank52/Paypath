from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.USER

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str
    mfa_code: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str
    full_name: Optional[str] = None
    mfa_required: bool = False

class MFASetupResponse(BaseModel):
    secret: str
    otpauth_url: str
    message: str

class MFAVerifyRequest(BaseModel):
    code: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    mfa_enabled: bool = False

    class Config:
        from_attributes = True
