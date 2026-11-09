from typing import Dict, Any, List
from app.agents.base import BaseAgent

class RiskAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="RiskAgent", role="Transaction Risk & Anomaly Detector")

    async def evaluate_risk(
        self,
        amount: float,
        merchant_name: str,
        recent_transactions: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        signals = []
        score = 0.05

        # 1. Large transaction detection
        if amount > 500.0:
            score += 0.40
            signals.append("HIGH_VALUE_TRANSACTION")
        elif amount > 200.0:
            score += 0.15
            signals.append("ELEVATED_VALUE_TRANSACTION")

        # 2. Duplicate detection check
        if recent_transactions:
            for past_tx in recent_transactions:
                if (
                    past_tx.get("merchant_name") == merchant_name and
                    abs(past_tx.get("amount", 0) - amount) < 0.01
                ):
                    score += 0.50
                    signals.append("POTENTIAL_DUPLICATE_PAYMENT_SIGNAL")
                    break

        risk_level = "LOW"
        if score >= 0.70:
            risk_level = "HIGH"
        elif score >= 0.35:
            risk_level = "MEDIUM"

        return {
            "risk_score": min(score, 1.0),
            "risk_level": risk_level,
            "signals": signals or ["NORMAL_VELOCITY_AND_VOLUME"],
            "explanation": f"Transaction evaluated with {risk_level} risk score ({score:.2f})."
        }

risk_agent = RiskAgent()
