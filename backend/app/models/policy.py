from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON
from app.models.base import TimeStampedModel

class MerchantPolicy(TimeStampedModel):
    __tablename__ = "merchant_policies"

    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    policy_type = Column(String(50), nullable=False) # REFUND, RETURN, WARRANTY, SPENDING
    raw_content = Column(Text, nullable=False)
    status = Column(String(50), default="PUBLISHED", nullable=False) # DRAFT, PUBLISHED, ARCHIVED
    version = Column(Integer, default=1, nullable=False)
    rules_json = Column(JSON, nullable=True) # Extracted deterministic rules

class PolicyChunk(TimeStampedModel):
    __tablename__ = "policy_chunks"

    policy_id = Column(String(36), ForeignKey("merchant_policies.id"), nullable=False, index=True)
    merchant_id = Column(String(36), ForeignKey("merchants.id"), nullable=False, index=True)
    section_title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    chunk_metadata = Column(JSON, nullable=True)
    embedding = Column(JSON, nullable=True) # Vector representation or fallback JSON array
