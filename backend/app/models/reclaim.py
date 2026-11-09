from sqlalchemy import Column, String, Text, Numeric, ForeignKey, JSON
from app.models.base import TimeStampedModel

class ReclaimCase(TimeStampedModel):
    __tablename__ = "reclaim_cases"

    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    issue_type = Column(String(50), nullable=False) # DAMAGED_ITEM, WRONG_ITEM, NOT_RECEIVED, DUPLICATE_CHARGE
    description = Column(Text, nullable=False)
    status = Column(String(50), default="OPEN", nullable=False) # OPEN, EVIDENCE_REQUIRED, UNDER_REVIEW, AI_RECOMMENDED, AWAITING_APPROVAL, APPROVED, RESOLVED, REJECTED
    proposed_resolution = Column(String(50), nullable=True) # FULL_REFUND, PARTIAL_REFUND, REPLACEMENT, NO_ACTION, ESCALATE
    recommended_amount = Column(Numeric(12, 2), nullable=True)
    confidence_score = Column(Numeric(4, 2), nullable=True)
    ai_reasoning = Column(Text, nullable=True)
    policy_citation = Column(JSON, nullable=True)
    approval_status = Column(String(50), default="PENDING", nullable=False) # PENDING, USER_APPROVED, MERCHANT_APPROVED, REJECTED

class Evidence(TimeStampedModel):
    __tablename__ = "evidence"

    reclaim_case_id = Column(String(36), ForeignKey("reclaim_cases.id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_url = Column(String(500), nullable=False)
    evidence_type = Column(String(50), default="PHOTO_DAMAGE", nullable=False) # PHOTO_DAMAGE, INVOICE, CORRESPONDENCE
    analysis_summary = Column(Text, nullable=True)
    confidence_score = Column(Numeric(4, 2), nullable=True)

