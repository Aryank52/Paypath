from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class GuardEvaluationRequest(BaseModel):
    amount: float = Field(gt=0)
    currency: str = Field(default="USD")
    merchant_name: str
    category: Optional[str] = "general"
    user_intent_id: Optional[str] = None

class GuardEvaluationResponse(BaseModel):
    decision: str # ALLOW, REVIEW, BLOCK, ESCALATE
    is_allowed: bool
    requires_approval: bool
    reason: str
    risk_score: float
    applied_rules: List[str]
    max_budget: Optional[float] = None
    requested_amount: float
