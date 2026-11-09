from typing import Dict, Any
from app.agents.base import BaseAgent
from app.paycore.verifier import payment_verifier

class VerificationAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="VerificationAgent", role="Authoritative Financial Ledger Auditor")

    async def verify_transaction_action(
        self,
        action_type: str,
        resource_id: str,
        expected_amount: float,
        expected_currency: str = "USD"
    ) -> Dict[str, Any]:
        if action_type == "REFUND":
            is_verified, details = await payment_verifier.verify_refund(
                refund_id=resource_id,
                expected_amount=expected_amount,
                expected_currency=expected_currency
            )
        else:
            is_verified, details = await payment_verifier.verify_capture(
                capture_id=resource_id,
                expected_amount=expected_amount,
                expected_currency=expected_currency
            )

        return {
            "resource_id": resource_id,
            "action_type": action_type,
            "is_verified": is_verified,
            "verification_status": "VERIFIED" if is_verified else "MISMATCH",
            "summary": (
                f"Independent read-back audit verified against PayPal Sandbox: {resource_id} is COMPLETED with exact amount {expected_currency} {expected_amount:.2f}."
                if is_verified else f"Verification mismatch for resource {resource_id}."
            ),
            "details": details
        }

verification_agent = VerificationAgent()

