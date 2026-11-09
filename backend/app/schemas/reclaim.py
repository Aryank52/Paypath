from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

class CreateReclaimCaseRequest(BaseModel):
    transaction_id: str
    issue_type: str = Field(default="DAMAGED_ITEM") # DAMAGED_ITEM, WRONG_ITEM, NOT_RECEIVED, DUPLICATE_CHARGE
    description: str = Field(..., description="Details regarding what happened with the order")

class EvidenceAnalysisResult(BaseModel):
    evidence_id: str
    file_name: str
    file_url: str
    evidence_type: str
    confidence_score: float
    analysis_summary: str

class ReclaimEvaluationResponse(BaseModel):
    case_id: str
    proposed_resolution: str # FULL_REFUND, PARTIAL_REFUND, REPLACEMENT, ESCALATE, NO_ACTION
    recommended_amount: float
    confidence_score: float
    ai_reasoning: str
    policy_citation: Optional[Dict[str, Any]] = None
    requires_approval: bool
    status: str

class ReclaimCaseResponse(BaseModel):
    id: str
    transaction_id: str
    user_id: str
    issue_type: str
    description: str
    status: str
    proposed_resolution: Optional[str] = None
    recommended_amount: Optional[float] = None
    confidence_score: Optional[float] = None
    ai_reasoning: Optional[str] = None
    policy_citation: Optional[Dict[str, Any]] = None
    approval_status: str
    created_at: datetime
    evidence_items: Optional[List[EvidenceAnalysisResult]] = None

    class Config:
        from_attributes = True

