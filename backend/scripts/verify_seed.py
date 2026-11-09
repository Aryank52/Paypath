"""
PayPath Database Seed Verification CLI Tool.
Usage:
  python -m backend.scripts.verify_seed
"""

import asyncio
import sys
import os

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import AsyncSessionLocal
from app.services.seed_service import verify_demo_data

async def run_verify():
    print("==================================================")
    print("PayPath PostgreSQL 16 Seed Verification")
    print("==================================================")
    async with AsyncSessionLocal() as session:
        stats = await verify_demo_data(session)
        print("\n--- PostgreSQL Authoritative Row Counts ---")
        for table, count in stats.items():
            print(f"  {table:25s}: {count:4d} rows")
        print("==================================================")
        return stats

def main():
    asyncio.run(run_verify())

if __name__ == "__main__":
    main()
