from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class TransactionEventResponse(BaseModel):
    id: str
    event_type: str
    actor: str
    description: str
    payload: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TransactionResponse(BaseModel):
    id: str
    user_id: str
    merchant_id: Optional[str] = None
    merchant_name: str
    paypal_order_id: Optional[str] = None
    paypal_capture_id: Optional[str] = None
    amount: float
    currency: str
    status: str
    verification_status: str
    risk_score: float
    risk_level: str
    source_type: Optional[str] = "PAYPAL_SANDBOX"
    ai_summary: Optional[str] = None
    item_description: Optional[str] = None
    created_at: datetime
    events: Optional[List[TransactionEventResponse]] = None
    meta_info: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class SubscriptionResponse(BaseModel):
    id: str
    merchant_name: str
    amount: float
    currency: str
    billing_interval: str
    last_payment_date: Optional[str] = None
    next_expected_date: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)

class SharedFeedItem(BaseModel):
    public_reference: str
    merchant_name: str
    item: str
    amount: float
    currency: str
    payment_state: str
    risk_level: str
    verification_status: str
    source: str
    ai_summary: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SharedFeedResponse(BaseModel):
    total_records: int
    page: int
    limit: int
    items: List[SharedFeedItem]
    provenance: str = "RENDER_POSTGRESQL_16"

