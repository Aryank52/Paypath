from sqlalchemy import Column, String, Text, Boolean, ForeignKey, JSON
from app.models.base import TimeStampedModel

class Notification(TimeStampedModel):
    __tablename__ = "notifications"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False) # PAYMENT_APPROVAL_REQUIRED, REFUND_COMPLETED, ANOMALY_DETECTED, etc.
    is_read = Column(Boolean, default=False, nullable=False)
    action_url = Column(String(255), nullable=True)
    payload = Column(JSON, nullable=True)

