from typing import Dict, Any, List
from app.agents.base import BaseAgent

# Demo product catalog adhering to Channel3 normalization standards
SAMPLE_CATALOG = [
    {
        "id": "prod_nova_anc_pro",
        "title": "NovaSound ANC Pro Wireless Headphones",
        "category": "headphones",
        "price": 89.00,
        "currency": "USD",
        "merchant_name": "Nova Electronics",
        "rating": 4.8,
        "features": ["Active Noise Cancellation", "40hr Battery Life", "Foldable Travel Case"],
        "in_stock": True,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80"
    },
    {
        "id": "prod_urban_flow_7",
        "title": "UrbanFit AeroPods Wireless Earbuds",
        "category": "headphones",
        "price": 69.99,
        "currency": "USD",
        "merchant_name": "UrbanFit",
        "rating": 4.5,
        "features": ["Compact Charging Case", "Sweat Resistant", "Quick Pairing"],
        "in_stock": True,
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&q=80"
    },
    {
        "id": "prod_audio_max_studio",
        "title": "StudioMaster Pro Over-Ear Reference Monitor",
        "category": "headphones",
        "price": 189.00,
        "currency": "USD",
        "merchant_name": "MediaNest",
        "rating": 4.9,
        "features": ["High Resolution Audio", "Velvet Ear Cushions"],
        "in_stock": True,
        "image_url": "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=500&q=80"
    }
]

class ShoppingAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ShoppingAgent", role="Product Discovery & Proposal Generator")

    async def search_and_recommend(
        self,
        category: str = "headphones",
        budget: float = 100.0,
        purpose: str = "travel"
    ) -> List[Dict[str, Any]]:
        recommendations = []
        cat_lower = category.lower() if category else ""
        for item in SAMPLE_CATALOG:
            item_cat = item["category"].lower()
            # Category match (audio, headphones, sound)
            if cat_lower:
                match = (cat_lower == item_cat) or (cat_lower in ["audio", "sound"] and item_cat == "headphones")
                if not match:
                    continue

            # Budget match
            is_under_budget = budget is None or item["price"] <= budget

            rec = dict(item)
            rec["matches_budget"] = is_under_budget
            rec["ai_recommendation_score"] = 0.95 if is_under_budget else 0.40
            rec["recommendation_rationale"] = (
                f"Matches travel requirements with Active Noise Cancellation at ${item['price']:.2f} "
                f"(within ${budget:.2f} budget)." if is_under_budget else f"Exceeds target budget of ${budget:.2f}."
            )
            recommendations.append(rec)

        recommendations.sort(key=lambda x: x["ai_recommendation_score"], reverse=True)
        return recommendations

shopping_agent = ShoppingAgent()

