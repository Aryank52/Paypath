from sqlalchemy import Column, String, Boolean, Enum, DateTime, Integer
from app.models.base import TimeStampedModel
import enum

class UserRole(str, enum.Enum):
    USER = "USER"
    MERCHANT_USER = "MERCHANT_USER"
    MERCHANT_ADMIN = "MERCHANT_ADMIN"
    PLATFORM_ADMIN = "PLATFORM_ADMIN"

class User(TimeStampedModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    mobile_number = Column(String(32), nullable=True)
    preferred_currency = Column(String(3), default="USD", nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Email Verification
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(128), nullable=True)
    email_verification_expires = Column(DateTime(timezone=True), nullable=True)
    
    # MFA / 2FA Security
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(64), nullable=True)
    
    # Password Reset Security
    password_reset_token = Column(String(128), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Brute Force Protection
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)

