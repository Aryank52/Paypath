from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class CreateOrderRequest(BaseModel):
    amount: float = Field(gt=0, description="Order amount")
    currency: str = Field(default="USD", max_length=3)
    merchant_id: Optional[str] = None
    merchant_name: str = Field(default="Nova Electronics")
    item_description: str = Field(default="NovaSound ANC Pro Headphones")
    user_intent_id: Optional[str] = None

class CreateOrderResponse(BaseModel):
    order_id: str
    status: str
    approve_url: Optional[str] = None
    amount: float
    currency: str

class CaptureOrderRequest(BaseModel):
    order_id: str

class CaptureOrderResponse(BaseModel):
    capture_id: str
    order_id: str
    status: str
    amount: float
    currency: str
    verification_status: str

class RefundRequest(BaseModel):
    transaction_id: str
    amount: float = Field(gt=0, description="Refund amount")
    currency: str = Field(default="USD", max_length=3)
    reason: str = Field(default="Customer reported damaged item")
    reclaim_case_id: Optional[str] = None

class RefundResponse(BaseModel):
    refund_id: str
    capture_id: str
    status: str
    amount: float
    currency: str
    verification_status: str
    is_verified: bool

class VerificationResultSchema(BaseModel):
    is_verified: bool
    resource_id: str
    expected_amount: float
    actual_amount: float
    expected_currency: str
    actual_currency: str
    paypal_status: str
    details: Dict[str, Any]

