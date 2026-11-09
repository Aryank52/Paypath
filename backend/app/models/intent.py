from sqlalchemy import Column, String, Text, Numeric, Boolean, ForeignKey
from app.models.base import TimeStampedModel

class PurchaseIntent(TimeStampedModel):
    __tablename__ = "purchase_intents"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    raw_prompt = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    purpose = Column(String(255), nullable=True)
    budget_amount = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    approval_required = Column(Boolean, default=True, nullable=False)
    autonomy_level = Column(String(50), default="RESTRICTED", nullable=False) # RESTRICTED, SUPERVISED, AUTONOMOUS
    status = Column(String(50), default="ACTIVE", nullable=False) # ACTIVE, FULFILLED, EXPIRED, CANCELLED

