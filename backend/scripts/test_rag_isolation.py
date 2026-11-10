"""
PayPath RAG Verification and Multi-Tenant Isolation Test Script.
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.rag.vector_store import vector_store

async def run_rag_verification():
    async with AsyncSessionLocal() as session:
        count = await vector_store.load_from_db(session)
        print(f"Total chunks loaded from PostgreSQL 16: {count}")
        
        # 1. Single Merchant Query (Nova Electronics)
        query = "damaged in transit return defective replacement"
        results = vector_store.search(query, merchant_id="mch_nova_electronics", top_k=2)
        print("\n=== Nova Electronics Query Results ===")
        for idx, r in enumerate(results, 1):
            print(f"[{idx}] Merchant: {r['merchant_id']}")
            print(f"    Section : {r['section_title']}")
            print(f"    Score   : {r.get('similarity_score', 0):.4f}")
            print(f"    Snippet : {r['content'][:140]}...")
            
        # 2. Multi-Tenant Isolation Proof (UrbanFit vs Nova)
        print("\n=== Multi-Tenant Boundary Verification ===")
        results_urban = vector_store.search("electronics headphones damage return", merchant_id="mch_urban_fit", top_k=5)
        leaks = [r for r in results_urban if r['merchant_id'] != 'mch_urban_fit']
        print(f"Query for UrbanFit returned {len(results_urban)} chunks.")
        print(f"Cross-tenant leaks detected: {len(leaks)}")
        assert len(leaks) == 0, "Security violation: Cross-tenant leak detected!"
        print("PASS: 100% Tenant Isolation verified at retrieval layer.")

if __name__ == "__main__":
    asyncio.run(run_rag_verification())
