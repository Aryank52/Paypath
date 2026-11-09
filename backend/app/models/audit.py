from sqlalchemy import Column, String, ForeignKey, JSON
from app.models.base import TimeStampedModel

class AuditLog(TimeStampedModel):
    __tablename__ = "audit_logs"

    action = Column(String(100), nullable=False, index=True)
    actor_type = Column(String(50), nullable=False) # USER, AGENT, SYSTEM
    actor_id = Column(String(100), nullable=True)
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(100), nullable=False, index=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)

