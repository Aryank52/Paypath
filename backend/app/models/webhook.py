from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, UniqueConstraint
from app.models.base import TimeStampedModel, generate_uuid

class WebhookEvent(TimeStampedModel):
    """
    Authoritative PostgreSQL record for PayPal Webhook Events.
    Enforces deduplication, cryptographic payload tracking, and auditability.
    """
    __tablename__ = "webhook_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    paypal_event_id = Column(String(128), unique=True, nullable=False, index=True)
    transmission_id = Column(String(128), nullable=True, index=True)
    event_type = Column(String(128), nullable=False, index=True)
    resource_type = Column(String(64), nullable=True)
    resource_id = Column(String(128), nullable=True, index=True)
    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=True, index=True)
    status = Column(String(64), default="WEBHOOK_RECEIVED", nullable=False, index=True)
    # Verification states: WEBHOOK_RECEIVED, WEBHOOK_AUTHENTICATED, RECONCILIATION_REQUIRED, PAYPAL_READ_BACK, VERIFIED, FAILED
    received_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    payload_hash = Column(String(64), nullable=True)  # SHA-256 of raw webhook body
    payload = Column(JSON, nullable=True)  # Sanitized/redacted payload
    processing_error = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("paypal_event_id", name="uq_webhook_events_paypal_event_id"),
    )
