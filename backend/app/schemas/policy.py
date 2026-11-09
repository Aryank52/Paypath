from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

class PolicyUploadRequest(BaseModel):
    merchant_id: str
    title: str
    policy_type: str = "REFUND" # REFUND, RETURN, WARRANTY, SPENDING
    content: str
    rules: Optional[Dict[str, Any]] = None

class PolicyQueryRequest(BaseModel):
    merchant_id: Optional[str] = None
    query: str
    top_k: int = 3

class PolicyCitationSchema(BaseModel):
    merchant_name: str
    policy_title: str
    section: str
    excerpt: str
    applicability: str
    rules: Optional[Dict[str, Any]] = None

class PolicyResponse(BaseModel):
    id: str
    merchant_id: str
    title: str
    policy_type: str
    raw_content: str
    status: str
    version: int
    rules_json: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

