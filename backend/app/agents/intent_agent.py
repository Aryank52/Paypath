import re
from typing import Dict, Any, Optional
from app.agents.base import BaseAgent

class IntentAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="IntentAgent", role="Purchase Intelligence & Intent Extraction")

    async def parse_intent(self, prompt: str) -> Dict[str, Any]:
        lower = prompt.lower()

        # 1. Extract amount / budget
        amount: Optional[float] = None
        amount_match = re.search(r'(?:for|\$|under|below|less than|max|budget of)\s*(\d+(?:\.\d{2})?)', lower)
        if not amount_match:
            amount_match = re.search(r'(\d+(?:\.\d{2})?)\s*(?:dollars|bucks|usd|\$)', lower)
        if amount_match:
            raw_val = float(amount_match.group(1))
            amount = int(raw_val) if raw_val.is_integer() else raw_val

        # 2. Extract product and category
        category = "electronics"
        product = "general_item"
        if "headphone" in lower or "earphone" in lower or "earbud" in lower or "audio" in lower:
            category = "headphones"
            product = "headphones"
        elif "laptop" in lower or "computer" in lower:
            category = "laptop"
            product = "laptop"
        elif "watch" in lower or "fitness" in lower:
            category = "wearables"
            product = "smartwatch"
        elif "shoes" in lower or "clothing" in lower:
            category = "apparel"
            product = "shoes"

        # 3. Extract issue if post-purchase
        issue: Optional[str] = None
        if "damage" in lower:
            issue = "damaged"
        elif "defect" in lower:
            issue = "defective"
        elif "broken" in lower or "crack" in lower:
            issue = "broken"
        elif "duplicate" in lower:
            issue = "duplicate_charge"
        elif "stolen" in lower or "fraud" in lower:
            issue = "unauthorized"

        # 4. Classify intent
        if issue or "bought" in lower or "purchased" in lower or "refund" in lower or "return" in lower or "dispute" in lower:
            intent_type = "post_purchase_resolution"
        else:
            intent_type = "purchase_search"

        # 5. Extract purpose
        purpose = "general"
        if "travel" in lower or "flight" in lower or "commute" in lower:
            purpose = "travel"
        elif "work" in lower or "office" in lower:
            purpose = "work"
        elif "gym" in lower or "workout" in lower or "running" in lower:
            purpose = "fitness"

        # 6. Extract autonomy & approval flags
        approval_required = True
        if "automatically purchase" in lower or "buy immediately" in lower:
            autonomy = "SUPERVISED"
        else:
            autonomy = "RESTRICTED"

        return {
            "intent": intent_type,
            "category": category,
            "product": product,
            "amount": amount,
            "budget": float(amount) if amount is not None else None,
            "currency": "USD",
            "issue": issue,
            "purpose": purpose,
            "approval_required": approval_required,
            "autonomy": autonomy,
            "raw_prompt": prompt
        }

intent_agent = IntentAgent()

