from typing import Dict, Any, Optional
from pydantic import BaseModel

class SpendPolicyRule(BaseModel):
    max_amount_per_transaction: float = 300.0
    auto_approval_threshold: float = 50.0
    daily_budget_limit: float = 1000.0
    restricted_categories: list[str] = ["gambling", "crypto", "weapons"]
    flagged_merchants: list[str] = ["untrusted_vendor", "shady_dropship"]

class RefundPolicyRule(BaseModel):
    return_window_days: int = 30
    damaged_item_eligible: bool = True
    partial_refund_max_pct: float = 80.0
    max_auto_refund: float = 100.0
    human_approval_required: bool = True
