from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.user import UserRole

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    mobile_number: Optional[str] = None
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

class EmailVerificationRequest(BaseModel):
    token: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class UserProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    mobile_number: Optional[str] = None
    preferred_currency: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    mobile_number: Optional[str] = None
    preferred_currency: str = "USD"
    role: str
    is_active: bool
    email_verified: bool = False
    mfa_enabled: bool = False

    model_config = ConfigDict(from_attributes=True)

class PersonaSwitchRequest(BaseModel):
    persona: str  # "shopper", "merchant", "platform_admin"

class PersonaSwitchResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str
    active_persona: str
    allowed_personas: list[str]
    full_name: Optional[str] = None
    tenant: Optional[str] = None
    permissions: list[str]

class DemoSessionRequest(BaseModel):
    persona: Optional[str] = "shopper"  # "shopper", "merchant", "platform_admin"

class DemoSessionResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str
    active_persona: str
    allowed_personas: list[str]
    full_name: Optional[str] = None
    is_demo: bool = True
