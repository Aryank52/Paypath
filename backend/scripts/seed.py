"""
PayPath Database Seed CLI Tool.
Usage:
  python -m backend.scripts.seed --action=seed
  python -m backend.scripts.seed --action=reset
  python -m backend.scripts.seed --action=verify
"""

import argparse
import asyncio
import sys
import os

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import AsyncSessionLocal
from app.services.seed_service import seed_demo_data, reset_demo_data, verify_demo_data
from app.ml.train import train_and_register_models

async def run(action: str):
    print("==================================================")
    print("PayPath PostgreSQL 16 Data Seeder & Verifier")
    print(f"Action requested: {action.upper()}")
    print("==================================================")

    async with AsyncSessionLocal() as session:
        if action == "reset":
            print("Wiping existing data and re-seeding full database...")
            stats = await seed_demo_data(session, force_reset=True)
            print("Retraining ML models on seeded transactions...")
            await train_and_register_models(session)
            print("\nDatabase cleanly reset and re-seeded!")
        elif action == "seed":
            print("Running idempotent seed...")
            stats = await seed_demo_data(session, force_reset=False)
            print("Ensuring active ML models registered...")
            await train_and_register_models(session)
            print("\nIdempotent seed completed!")
        elif action == "verify":
            print("Verifying current PostgreSQL row counts...")
            stats = await verify_demo_data(session)
        else:
            print(f"Unknown action: {action}. Choose from: seed, reset, verify")
            return

        print("\n--- Current PostgreSQL Table Row Counts ---")
        for table, count in stats.items():
            print(f"  {table:25s}: {count:4d} rows")
        print("==================================================")

def main():
    parser = argparse.ArgumentParser(description="PayPath PostgreSQL Seed Manager")
    parser.add_argument(
        "--action",
        choices=["seed", "reset", "verify"],
        default="seed",
        help="Action to perform: seed (idempotent), reset (clean wipe + seed), verify (read row counts)",
    )
    args = parser.parse_args()
    asyncio.run(run(args.action))

if __name__ == "__main__":
    main()
