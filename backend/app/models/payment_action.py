from sqlalchemy import Column, String, Text, Numeric, Boolean, ForeignKey, JSON
from app.models.base import TimeStampedModel

class PaymentAction(TimeStampedModel):
    __tablename__ = "payment_actions"

    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False) # CAPTURE, REFUND, AUTHORIZE
    requested_amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    idempotency_key = Column(String(255), unique=True, index=True, nullable=False)
    state = Column(String(50), default="PROPOSED", nullable=False) # PROPOSED, AWAITING_APPROVAL, APPROVED, EXECUTING, EXECUTED, VERIFIED, FAILED, REJECTED
    paypal_reference_id = Column(String(100), nullable=True) # e.g. PayPal refund ID or capture ID
    error_message = Column(Text, nullable=True)
    meta_info = Column(JSON, nullable=True)

class PaymentVerification(TimeStampedModel):
    __tablename__ = "payment_verifications"

    payment_action_id = Column(String(36), ForeignKey("payment_actions.id"), nullable=False, index=True)
    paypal_resource_id = Column(String(100), nullable=False)
    expected_amount = Column(Numeric(12, 2), nullable=False)
    actual_amount = Column(Numeric(12, 2), nullable=False)
    expected_currency = Column(String(3), nullable=False)
    actual_currency = Column(String(3), nullable=False)
    is_verified = Column(Boolean, nullable=False)
    verification_details = Column(JSON, nullable=True)
