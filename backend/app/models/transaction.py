from sqlalchemy import Column, String, Text, Numeric, ForeignKey, JSON
from app.models.base import TimeStampedModel

class Transaction(TimeStampedModel):
    __tablename__ = "transactions"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=True, index=True)
    merchant_name = Column(String(255), nullable=False)
    paypal_order_id = Column(String(100), index=True, nullable=True)
    paypal_capture_id = Column(String(100), index=True, nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(String(50), default="CREATED", nullable=False) # CREATED, CAPTURED, REFUNDED, PARTIALLY_REFUNDED, FAILED
    verification_status = Column(String(50), default="PENDING", nullable=False) # PENDING, VERIFIED, MISMATCH, FAILED
    risk_score = Column(Numeric(4, 2), default=0.0, nullable=False)
    risk_level = Column(String(20), default="LOW", nullable=False) # LOW, MEDIUM, HIGH
    ai_summary = Column(Text, nullable=True)
    item_description = Column(Text, nullable=True)
    meta_info = Column(JSON, nullable=True)

    @property
    def source_type(self) -> str:
        if self.meta_info and isinstance(self.meta_info, dict):
            if "source_type" in self.meta_info:
                return str(self.meta_info["source_type"])
            if self.meta_info.get("is_synthetic") or (self.id and self.id.startswith("tx_")):
                return "DEMO_SEED"
        return "PAYPAL_SANDBOX"

class TransactionEvent(TimeStampedModel):
    __tablename__ = "transaction_events"

    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False) # INTENT_CREATED, ORDER_CREATED, PAYMENT_CAPTURED, REFUND_REQUESTED, etc.
    actor = Column(String(100), nullable=False) # SYSTEM, USER, PAYPAL, AGENT
    description = Column(Text, nullable=False)
    payload = Column(JSON, nullable=True)

class Subscription(TimeStampedModel):
    __tablename__ = "subscriptions"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    merchant_name = Column(String(255), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    billing_interval = Column(String(50), default="MONTHLY", nullable=False)
    last_payment_date = Column(String(50), nullable=True)
    next_expected_date = Column(String(50), nullable=True)
    status = Column(String(50), default="ACTIVE", nullable=False)

