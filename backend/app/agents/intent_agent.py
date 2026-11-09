import re
from typing import Dict, Any, Optional
from app.agents.base import BaseAgent

class IntentAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="IntentAgent", role="Purchase Intelligence & Intent Extraction")

    async def parse_intent(self, prompt: str) -> Dict[str, Any]:
        lower = prompt.lower()

        # 1. Extract budget
        budget: Optional[float] = None
        budget_match = re.search(r'(?:under|below|less than|max|budget of|\$)\s*(\d+(?:\.\d{2})?)', lower)
        if budget_match:
            budget = float(budget_match.group(1))

        # 2. Extract category
        category = "electronics"
        if "headphone" in lower or "earphone" in lower or "earbud" in lower or "audio" in lower:
            category = "headphones"
        elif "laptop" in lower or "computer" in lower:
            category = "laptop"
        elif "watch" in lower or "fitness" in lower:
            category = "wearables"
        elif "shoes" in lower or "clothing" in lower:
            category = "apparel"

        # 3. Extract purpose
        purpose = "general"
        if "travel" in lower or "flight" in lower or "commute" in lower:
            purpose = "travel"
        elif "work" in lower or "office" in lower:
            purpose = "work"
        elif "gym" in lower or "workout" in lower or "running" in lower:
            purpose = "fitness"

        # 4. Extract autonomy & approval flags
        approval_required = True
        if "automatically purchase" in lower or "buy immediately" in lower:
            autonomy = "SUPERVISED"
        else:
            autonomy = "RESTRICTED"

        return {
            "category": category,
            "purpose": purpose,
            "budget": budget,
            "currency": "USD",
            "approval_required": approval_required,
            "autonomy": autonomy,
            "raw_prompt": prompt
        }

intent_agent = IntentAgent()
