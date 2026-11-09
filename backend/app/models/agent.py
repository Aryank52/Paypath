from sqlalchemy import Column, String, Integer, JSON, ForeignKey
from app.models.base import TimeStampedModel

class AgentRun(TimeStampedModel):
    __tablename__ = "agent_runs"
    
    agent_name = Column(String(100), nullable=False) # "IntentAgent", "RiskAgent", "ResolutionAgent", etc.
    session_id = Column(String(100), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), default="COMPLETED", nullable=False)
    latency_ms = Column(Integer, default=0, nullable=False)
    decision_summary = Column(String(1000), nullable=True)
    meta_info = Column(JSON, default=dict)

class AgentToolCall(TimeStampedModel):
    __tablename__ = "agent_tool_calls"
    
    run_id = Column(String(36), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=True)
    agent_name = Column(String(100), nullable=False)
    tool_name = Column(String(100), nullable=False)
    input_payload = Column(JSON, default=dict)
    output_payload = Column(JSON, default=dict)
    status = Column(String(50), default="SUCCESS", nullable=False)
    duration_ms = Column(Integer, default=0, nullable=False)
    is_approved = Column(String(50), default="AUTO_ALLOWED", nullable=False)

