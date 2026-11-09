import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import init_db, engine
from app.models import (
    User, Merchant, MerchantPolicy, PolicyChunk, PurchaseIntent,
    Transaction, TransactionEvent, PaymentAction, PaymentVerification,
    ReclaimCase, Evidence, AuditLog, Subscription, Notification
)
from sqlalchemy import text

async def main():
    print("Connecting to PostgreSQL and creating tables...")
    await init_db()
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"))
        tables = [row[0] for row in res.fetchall()]
        print(f"Successfully verified {len(tables)} tables in PostgreSQL:")
        for t in tables:
            print(f"  - {t}")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())

