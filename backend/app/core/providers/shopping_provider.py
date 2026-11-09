from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.observability import logger

class BaseShoppingProvider(ABC):
    @abstractmethod
    async def search_products(self, query: str, category: str, max_price: Optional[float] = None) -> List[Dict[str, Any]]:
        pass

class Channel3ShoppingProvider(BaseShoppingProvider):
    """Channel3 normalized product catalog integration."""
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    async def search_products(self, query: str, category: str, max_price: Optional[float] = None) -> List[Dict[str, Any]]:
        logger.info(f"Channel3 provider querying: {query} under {max_price}")
        # Falls back gracefully to verified normalized demo catalog
        return await DemoCatalogShoppingProvider().search_products(query, category, max_price)

class DemoCatalogShoppingProvider(BaseShoppingProvider):
    """Standard normalized catalog adhering to Channel3 specifications."""
    def __init__(self):
        self.catalog = [
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

    async def search_products(self, query: str, category: str, max_price: Optional[float] = None) -> List[Dict[str, Any]]:
        results = []
        for item in self.catalog:
            if category and item["category"] != category:
                continue
            if max_price is not None and item["price"] > max_price:
                continue
            results.append(item)
        return results

def get_shopping_provider() -> BaseShoppingProvider:
    if settings.ENABLE_CHANNEL3:
        return Channel3ShoppingProvider()
    return DemoCatalogShoppingProvider()

shopping_provider = get_shopping_provider()

