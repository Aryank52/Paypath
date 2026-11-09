from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class IntentParseRequest(BaseModel):
    prompt: str = Field(..., description="Natural language purchase or search intent")

class IntentResponse(BaseModel):
    id: Optional[str] = None
    category: Optional[str] = None
    purpose: Optional[str] = None
    budget: Optional[float] = None
    currency: str = "USD"
    approval_required: bool = True
    autonomy: str = "RESTRICTED"
    raw_prompt: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

