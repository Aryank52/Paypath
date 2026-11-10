import os
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.observability import logger

class LLMProviderError(Exception):
    """Raised when an LLM provider fails and fallback is disabled or error simulation is active."""
    pass

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_structured(self, prompt: str, schema_name: str, allow_mock_fallback: bool = True) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        pass

class MockLLMProvider(BaseLLMProvider):
    """Deterministic, resilient mock provider for offline local development and test stability."""
    
    async def check_health(self) -> Dict[str, Any]:
        return {
            "status": "MOCK",
            "provider": "mock",
            "model": "deterministic-mock-v1",
            "configured": False,
            "connected": True,
        }

    async def generate_structured(self, prompt: str, schema_name: str, allow_mock_fallback: bool = True) -> Dict[str, Any]:
        logger.info(f"MockLLMProvider invoked for schema: {schema_name}")
        lower = prompt.lower()
        
        # Check for post-purchase resolution / damage intent
        if any(w in lower for w in ["damage", "defect", "broken", "bought", "purchased", "refund", "resolution"]):
            amount = 89.0
            amount_match = re.search(r'\$(\d+(?:\.\d{2})?)|\b(\d+(?:\.\d{2})?)\s*(?:dollars|usd)', lower)
            if amount_match:
                amount = float(amount_match.group(1) or amount_match.group(2))
            
            product = "headphones" if "headphone" in lower or "earphone" in lower else "item"
            issue = "damaged" if "damage" in lower else ("defective" if "defect" in lower else "general_issue")
            
            return {
                "intent": "post_purchase_resolution",
                "product": product,
                "amount": int(amount) if amount.is_integer() else amount,
                "currency": "USD",
                "issue": issue,
            }

        return {
            "intent": "travel_headphones",
            "budget": 100.0,
            "category": "headphones",
            "rationale": "High traveler confidence and active noise cancellation."
        }

class GeminiLLMProvider(BaseLLMProvider):
    """Official Google Gemini API provider using official API key and endpoint."""
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model
        self.simulate_failure = False

    async def check_health(self) -> Dict[str, Any]:
        if self.simulate_failure:
            return {
                "status": "ERROR",
                "provider": "gemini",
                "model": self.model,
                "configured": bool(self.api_key),
                "connected": False,
                "error": "Simulated provider failure",
            }

        if not self.api_key:
            return {
                "status": "NOT_CONFIGURED",
                "provider": "gemini",
                "model": self.model,
                "configured": False,
                "connected": False,
            }

        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}?key={self.api_key}"
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    return {
                        "status": "CONNECTED",
                        "provider": "gemini",
                        "model": self.model,
                        "configured": True,
                        "connected": True,
                    }
                return {
                    "status": "ERROR",
                    "provider": "gemini",
                    "model": self.model,
                    "configured": True,
                    "connected": False,
                    "http_status": res.status_code,
                }
        except Exception as e:
            return {
                "status": "ERROR",
                "provider": "gemini",
                "model": self.model,
                "configured": True,
                "connected": False,
                "error": str(e),
            }

    async def generate_structured(self, prompt: str, schema_name: str, allow_mock_fallback: bool = True) -> Dict[str, Any]:
        if self.simulate_failure:
            if not allow_mock_fallback:
                raise LLMProviderError("Simulated LLM Provider Failure: provider unavailable.")
            logger.warning("Simulated failure active; falling back to MockLLMProvider.")
            return await MockLLMProvider().generate_structured(prompt, schema_name)

        if not self.api_key:
            if not allow_mock_fallback:
                raise LLMProviderError("Gemini API key is not configured in .env.")
            return await MockLLMProvider().generate_structured(prompt, schema_name)

        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": f"Respond in JSON matching schema {schema_name}:\n{prompt}"}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(url, json=payload)
                res.raise_for_status()
                data = res.json()
                import json
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except Exception as e:
            if not allow_mock_fallback:
                raise LLMProviderError(f"Gemini API request failed: {e}")
            logger.error(f"Gemini API request failed, falling back to mock provider: {e}")
            return await MockLLMProvider().generate_structured(prompt, schema_name)

def get_llm_provider() -> BaseLLMProvider:
    provider = getattr(settings, "LLM_PROVIDER", "gemini").lower()
    if provider == "mock":
        return MockLLMProvider()
    if settings.GEMINI_API_KEY:
        return GeminiLLMProvider(model=getattr(settings, "LLM_MODEL", "gemini-2.5-flash"))
    return MockLLMProvider()

llm_provider = get_llm_provider()

