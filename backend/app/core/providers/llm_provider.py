import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.observability import logger

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_structured(self, prompt: str, schema_name: str) -> Dict[str, Any]:
        pass

class MockLLMProvider(BaseLLMProvider):
    """Deterministic, resilient mock provider for offline local development and test stability."""
    async def generate_structured(self, prompt: str, schema_name: str) -> Dict[str, Any]:
        logger.info(f"MockLLMProvider invoked for schema: {schema_name}")
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

    async def generate_structured(self, prompt: str, schema_name: str) -> Dict[str, Any]:
        if not self.api_key:
            # Fall back to mock provider if no API key configured
            return await MockLLMProvider().generate_structured(prompt, schema_name)

        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": f"Respond in JSON matching {schema_name}:\n{prompt}"}]}],
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
            logger.error(f"Gemini API request failed, falling back to mock provider: {e}")
            return await MockLLMProvider().generate_structured(prompt, schema_name)

def get_llm_provider() -> BaseLLMProvider:
    if settings.GEMINI_API_KEY:
        return GeminiLLMProvider()
    return MockLLMProvider()

llm_provider = get_llm_provider()
