from typing import Dict, Any, List, Optional
from app.policies.rules import SpendPolicyRule, RefundPolicyRule
from app.core.observability import logger

class DeterministicPolicyEngine:
    """
    Evaluates financial proposals deterministically.
    AI may propose, but this engine holds deterministic authority over ALLOW / REVIEW / BLOCK.
    """

    def __init__(self, spend_rules: Optional[SpendPolicyRule] = None, refund_rules: Optional[RefundPolicyRule] = None):
        self.spend_rules = spend_rules or SpendPolicyRule()
        self.refund_rules = refund_rules or RefundPolicyRule()

    def evaluate_purchase(
        self,
        amount: float,
        merchant_name: str,
        category: str = "general",
        user_intent_budget: Optional[float] = None
    ) -> Dict[str, Any]:
        applied_rules: List[str] = []
        decision = "ALLOW"
        requires_approval = False
        reason = "Transaction complies with spending policies."
        risk_score = 0.05

        # 1. Blocked Category Check
        if category.lower() in [c.lower() for c in self.spend_rules.restricted_categories]:
            return {
                "decision": "BLOCK",
                "is_allowed": False,
                "requires_approval": False,
                "reason": f"Category '{category}' is prohibited by safety policy.",
                "risk_score": 0.95,
                "applied_rules": ["RESTRICTED_CATEGORY_RULE"],
                "max_budget": user_intent_budget or self.spend_rules.max_amount_per_transaction,
                "requested_amount": amount
            }

        # 2. Flagged Merchant Check
        if merchant_name.lower() in [m.lower() for m in self.spend_rules.flagged_merchants]:
            return {
                "decision": "BLOCK",
                "is_allowed": False,
                "requires_approval": False,
                "reason": f"Merchant '{merchant_name}' is on the restricted merchant list.",
                "risk_score": 0.90,
                "applied_rules": ["RESTRICTED_MERCHANT_RULE"],
                "max_budget": user_intent_budget or self.spend_rules.max_amount_per_transaction,
                "requested_amount": amount
            }

        # 3. User Intent Budget Check
        if user_intent_budget and amount > user_intent_budget:
            return {
                "decision": "BLOCK",
                "is_allowed": False,
                "requires_approval": False,
                "reason": f"Amount ${amount:.2f} exceeds user-configured intent budget of ${user_intent_budget:.2f}.",
                "risk_score": 0.65,
                "applied_rules": ["USER_INTENT_BUDGET_EXCEEDED"],
                "max_budget": user_intent_budget,
                "requested_amount": amount
            }

        # 4. Global Max Amount Check
        if amount > self.spend_rules.max_amount_per_transaction:
            decision = "REVIEW"
            requires_approval = True
            risk_score = 0.50
            applied_rules.append("GLOBAL_TRANSACTION_LIMIT_REVIEW")
            reason = f"Amount ${amount:.2f} exceeds single transaction threshold (${self.spend_rules.max_amount_per_transaction:.2f}). Requires review."

        # 5. Approval Gate
        if amount > self.spend_rules.auto_approval_threshold:
            requires_approval = True
            applied_rules.append("HUMAN_APPROVAL_THRESHOLD_RULE")
            if decision == "ALLOW":
                decision = "ALLOW"
                reason = f"Complies with spending limit. Requires explicit user authorization (${amount:.2f} > ${self.spend_rules.auto_approval_threshold:.2f})."

        return {
            "decision": decision,
            "is_allowed": decision != "BLOCK",
            "requires_approval": requires_approval,
            "reason": reason,
            "risk_score": risk_score,
            "applied_rules": applied_rules or ["STANDARD_PURCHASE_APPROVAL"],
            "max_budget": user_intent_budget or self.spend_rules.max_amount_per_transaction,
            "requested_amount": amount
        }

    def evaluate_refund(
        self,
        proposed_amount: float,
        transaction_amount: float,
        issue_type: str,
        transaction_age_days: int = 14,
        evidence_provided: bool = True
    ) -> Dict[str, Any]:
        """Evaluates whether a refund proposal adheres to merchant return policies."""
        applied_rules: List[str] = []

        # 1. Boundary Check: Cannot exceed original transaction amount
        if proposed_amount > transaction_amount:
            return {
                "decision": "BLOCK",
                "is_allowed": False,
                "requires_approval": False,
                "reason": f"Proposed refund (${proposed_amount:.2f}) exceeds total captured amount (${transaction_amount:.2f}).",
                "confidence_penalty": 1.0,
                "applied_rules": ["REFUND_EXCEEDS_TRANSACTION_AMOUNT"]
            }

        # 2. Return Window Check
        if transaction_age_days > self.refund_rules.return_window_days:
            return {
                "decision": "ESCALATE",
                "is_allowed": False,
                "requires_approval": True,
                "reason": f"Transaction age ({transaction_age_days} days) exceeds return window ({self.refund_rules.return_window_days} days). Escalated for manual review.",
                "confidence_penalty": 0.4,
                "applied_rules": ["RETURN_WINDOW_EXCEEDED"]
            }

        # 3. Evidence Requirement for Physical Damage
        if issue_type == "DAMAGED_ITEM" and not evidence_provided:
            return {
                "decision": "REVIEW",
                "is_allowed": False,
                "requires_approval": True,
                "reason": "Merchant policy requires photographic evidence for damaged goods.",
                "confidence_penalty": 0.3,
                "applied_rules": ["EVIDENCE_REQUIRED_RULE"]
            }

        # 4. Partial Refund Cap Check
        max_partial = transaction_amount * (self.refund_rules.partial_refund_max_pct / 100.0)
        if proposed_amount > max_partial and proposed_amount < transaction_amount:
            return {
                "decision": "REVIEW",
                "is_allowed": True,
                "requires_approval": True,
                "reason": f"Proposed refund (${proposed_amount:.2f}) exceeds standard partial refund cap of {self.refund_rules.partial_refund_max_pct}%.",
                "confidence_penalty": 0.1,
                "applied_rules": ["PARTIAL_REFUND_CAP_REVIEW"]
            }

        requires_approval = self.refund_rules.human_approval_required or proposed_amount > self.refund_rules.max_auto_refund
        applied_rules.append("MERCHANT_DAMAGE_POLICY_VALIDATED")

        return {
            "decision": "ALLOW",
            "is_allowed": True,
            "requires_approval": requires_approval,
            "reason": "Refund complies with merchant policy for damaged goods within the 30-day window.",
            "confidence_penalty": 0.0,
            "applied_rules": applied_rules
        }

policy_engine = DeterministicPolicyEngine()
