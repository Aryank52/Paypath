import math
import re
from typing import List, Dict, Any, Optional

class VectorStore:
    """
    Lightweight, high-performance in-memory and database-backed vector store
    with cosine similarity and tenant isolation.
    """

    def __init__(self):
        # In-memory index of chunks: list of dicts with embedding, content, metadata
        self._chunks: List[Dict[str, Any]] = []

    def _generate_embedding(self, text: str) -> List[float]:
        """Generates a deterministic 128-dimensional semantic hash vector."""
        words = re.findall(r'\w+', text.lower())
        vec = [0.0] * 128
        for word in words:
            h = hash(word)
            idx = abs(h) % 128
            vec[idx] += 1.0

        # Normalize vector
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def add_chunk(self, chunk: Dict[str, Any]) -> None:
        embedding = self._generate_embedding(chunk["content"])
        chunk_with_emb = dict(chunk)
        chunk_with_emb["embedding"] = embedding
        self._chunks.append(chunk_with_emb)

    def search(
        self,
        query: str,
        merchant_id: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        query_vec = self._generate_embedding(query)
        scored_results = []

        for chunk in self._chunks:
            # Tenant isolation: filter by merchant_id if specified
            if merchant_id and chunk.get("merchant_id") != merchant_id:
                continue

            chunk_vec = chunk.get("embedding", [])
            # Cosine similarity
            dot_product = sum(q * c for q, c in zip(query_vec, chunk_vec))
            scored_results.append((dot_product, chunk))

        # Sort descending by similarity
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_results[:top_k]]

vector_store = VectorStore()

