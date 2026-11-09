from sqlalchemy import Column, String, Boolean
from app.models.base import TimeStampedModel

class Merchant(TimeStampedModel):
    __tablename__ = "merchants"

    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    paypal_merchant_id = Column(String(100), nullable=True)
    support_email = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)

