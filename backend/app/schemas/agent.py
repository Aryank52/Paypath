from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

class AgentMessage(BaseModel):
    message_id: str
    from_agent: str
    to_agent: str
    message_type: str # INTENT_REQUEST, POLICY_CHECK, ACTION_PROPOSAL, etc.
    payload: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class AgentTraceStep(BaseModel):
    agent_name: str
    action: str
    status: str = "COMPLETED" # COMPLETED, RUNNING, FAILED
    summary: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class AgentWorkflowResult(BaseModel):
    workflow_id: str
    status: str
    steps: List[AgentTraceStep]
    final_output: Dict[str, Any]

