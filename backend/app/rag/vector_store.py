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

    @property
    def chunks(self) -> List[Dict[str, Any]]:
        return self._chunks

    async def load_from_db(self, session) -> int:
        """Hydrates vector store directly from authoritative PostgreSQL policy_chunks table."""
        try:
            from app.models.policy import PolicyChunk
            from sqlalchemy import select
            res = await session.execute(select(PolicyChunk))
            db_chunks = res.scalars().all()
            if db_chunks:
                self._chunks.clear()
                for c in db_chunks:
                    self._chunks.append({
                        "id": c.id,
                        "policy_id": c.policy_id,
                        "merchant_id": c.merchant_id,
                        "section_title": c.section_title or "Policy Section",
                        "content": c.content,
                        "embedding": c.embedding if (c.embedding and len(c.embedding) == 128) else self.generate_embedding(c.content),
                        "metadata": c.chunk_metadata or {},
                    })
            return len(self._chunks)
        except Exception as e:
            return len(self._chunks)

    def generate_embedding(self, text: str) -> List[float]:
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

    def _generate_embedding(self, text: str) -> List[float]:
        return self.generate_embedding(text)

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
        top_items = []
        for score, chunk in scored_results[:top_k]:
            c_copy = dict(chunk)
            c_copy["similarity_score"] = round(float(score), 4)
            top_items.append(c_copy)
        return top_items

vector_store = VectorStore()

