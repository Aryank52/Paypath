from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.transaction import Transaction, Subscription

class RecoveryService:
    """
    Payment Recovery Intelligence:
    Identifies duplicate payment anomalies, recurring subscription patterns,
    and missed recovery opportunities.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def detect_duplicates(self, user_id: str) -> List[Dict[str, Any]]:
        stmt = select(Transaction).where(Transaction.user_id == user_id).order_by(Transaction.created_at.desc())
        result = await self.db.execute(stmt)
        transactions = result.scalars().all()

        duplicates = []
        seen = {}
        for tx in transactions:
            key = (tx.merchant_name, float(tx.amount))
            if key in seen:
                prev_tx = seen[key]
                duplicates.append({
                    "original_transaction_id": prev_tx.id,
                    "duplicate_transaction_id": tx.id,
                    "merchant_name": tx.merchant_name,
                    "amount": float(tx.amount),
                    "currency": tx.currency,
                    "confidence_score": 0.95,
                    "signal_type": "IDENTICAL_AMOUNT_AND_MERCHANT",
                    "explanation": f"Detected matching charge of ${tx.amount:.2f} at {tx.merchant_name}. Potential duplicate billing.",
                    "recommended_action": "REQUEST_DUPLICATE_REFUND"
                })
            else:
                seen[key] = tx

        return duplicates

    async def list_subscriptions(self, user_id: str) -> List[Subscription]:
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
