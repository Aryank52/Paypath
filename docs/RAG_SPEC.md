# PayPath — RAG Specification (Retrieval-Augmented Generation)

## 1. Objective & Scope
The RAG subsystem in PayPath provides grounded, verifiable policy retrieval for the **Resolution Agent (RECLAIM)** and **Payment Guard**. It guarantees that refund eligibility, return windows, damage coverage, and spending constraints are backed by exact merchant policy citations.

---

## 2. Document Ingestion Pipeline

```text
Policy Document (.pdf / .md / .txt)
     │
     ▼
[Text Extraction & Normalization]
     │
     ▼
[Hierarchical Semantic Chunking] (Sections: Damaged Goods, Returns, Fees)
     │
     ▼
[Metadata Tagging] (merchant_id, policy_type, version, effective_date)
     │
     ▼
[Vector Embedding Generation] (768/1536-dim embeddings)
     │
     ▼
[PostgreSQL pgvector / HNSW Indexing]
```

---

## 3. Chunk Metadata Schema
```json
{
  "chunk_id": "chk_7d9e2a14",
  "policy_id": "pol_9281a10f",
  "merchant_id": "merch_nova_electronics",
  "merchant_name": "Nova Electronics",
  "policy_type": "REFUND",
  "section": "Damaged Goods & Transit Defects",
  "effective_date": "2026-01-01",
  "version": 1,
  "rules": {
    "return_window_days": 30,
    "damage_coverage": true,
    "partial_refund_max_pct": 80
  }
}
```

---

## 4. Tenant-Isolated Retrieval Strategy
All vector similarity queries strictly enforce tenant isolation:
```sql
SELECT section_title, content, metadata, 1 - (embedding <=> :query_vector) AS similarity
FROM policy_chunks
WHERE merchant_id = :merchant_id
ORDER BY embedding <=> :query_vector
LIMIT 3;
```
If `pgvector` is not available in an environment, the system automatically falls back to full-text search with metadata filtering (`tsvector` / keyword scoring).

---

## 5. Citation Formatting
Retrieved chunks injected into agent prompts are rendered as verified citations:
```text
[POLICY CITATION]
Merchant: Nova Electronics
Document: Return and Refund Policy v1
Section: Damaged Goods & Transit Defects
Relevant Excerpt: "If goods arrive with cosmetic or structural damage, customers are entitled to an immediate partial refund up to 75% or a free replacement if reported within 30 days of delivery."
Effective Date: 2026-01-01
Applicability: Applicable (Reported 14 days after purchase, physical damage confirmed)
```
