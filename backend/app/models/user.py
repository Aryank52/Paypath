from sqlalchemy import Column, String, Boolean, Enum
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
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

