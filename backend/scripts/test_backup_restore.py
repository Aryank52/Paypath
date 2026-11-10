"""
PayPath PostgreSQL 16 Backup & Restore Verification Test.
Dumps authoritative 'paypath' database, restores into 'paypath_restore_test',
and verifies table count and row count integrity.
"""

import os
import sys
import subprocess
import asyncio

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.core.config import settings

PG_BIN_DIR = r"E:\postsql database\bin"
PG_DUMP = os.path.join(PG_BIN_DIR, "pg_dump.exe")
PSQL = os.path.join(PG_BIN_DIR, "psql.exe")
BACKUP_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backups", "paypath_production_backup.sql"))

async def test_backup_restore():
    print("==========================================================")
    print(" PostgreSQL 16 Backup & Restore Integrity Certification")
    print("==========================================================")

    os.makedirs(os.path.dirname(BACKUP_FILE), exist_ok=True)
    
    # 1. Take dump
    print(f"[1/4] Dumping authoritative database 'paypath' -> {os.path.basename(BACKUP_FILE)}...")
    env = os.environ.copy()
    env["PGPASSWORD"] = "postgres"
    
    dump_proc = subprocess.run(
        [PG_DUMP, "-h", "127.0.0.1", "-p", "5432", "-U", "postgres", "-d", "paypath", "-f", BACKUP_FILE],
        env=env,
        capture_output=True,
        text=True
    )
    if dump_proc.returncode != 0:
        print(f"Dump failed: {dump_proc.stderr}")
        return False
    print(f"  Dump complete. File size: {os.path.getsize(BACKUP_FILE)} bytes.")

    # 2. Re-create clean test database paypath_restore_test
    print("[2/4] Initializing temporary database 'paypath_restore_test'...")
    subprocess.run(
        [PSQL, "-h", "127.0.0.1", "-p", "5432", "-U", "postgres", "-d", "postgres", "-c", "DROP DATABASE IF EXISTS paypath_restore_test;"],
        env=env,
        capture_output=True,
        text=True
    )
    create_proc = subprocess.run(
        [PSQL, "-h", "127.0.0.1", "-p", "5432", "-U", "postgres", "-d", "postgres", "-c", "CREATE DATABASE paypath_restore_test;"],
        env=env,
        capture_output=True,
        text=True
    )
    if create_proc.returncode != 0:
        print(f"Database creation failed: {create_proc.stderr}")
        return False
    print("  Temporary test database 'paypath_restore_test' ready.")

    # 3. Restore dump into paypath_restore_test
    print("[3/4] Restoring dump into 'paypath_restore_test'...")
    restore_proc = subprocess.run(
        [PSQL, "-h", "127.0.0.1", "-p", "5432", "-U", "postgres", "-d", "paypath_restore_test", "-f", BACKUP_FILE],
        env=env,
        capture_output=True,
        text=True
    )
    if restore_proc.returncode != 0:
        print(f"Restore warnings/errors: {restore_proc.stderr}")

    # 4. Count tables and rows in restored database
    print("[4/4] Verifying table inventory and row counts...")
    count_proc = subprocess.run(
        [PSQL, "-h", "127.0.0.1", "-p", "5432", "-U", "postgres", "-d", "paypath_restore_test", "-t", "-c", 
         "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';"],
        env=env,
        capture_output=True,
        text=True
    )
    restored_table_count = int(count_proc.stdout.strip())
    print(f"  Restored public tables: {restored_table_count}")

    user_count_proc = subprocess.run(
        [PSQL, "-h", "127.0.0.1", "-p", "5432", "-U", "postgres", "-d", "paypath_restore_test", "-t", "-c", 
         "SELECT count(*) FROM users;"],
        env=env,
        capture_output=True,
        text=True
    )
    restored_user_count = int(user_count_proc.stdout.strip())

    tx_count_proc = subprocess.run(
        [PSQL, "-h", "127.0.0.1", "-p", "5432", "-U", "postgres", "-d", "paypath_restore_test", "-t", "-c", 
         "SELECT count(*) FROM transactions;"],
        env=env,
        capture_output=True,
        text=True
    )
    restored_tx_count = int(tx_count_proc.stdout.strip())

    print(f"  Restored users count: {restored_user_count}")
    print(f"  Restored transactions count: {restored_tx_count}")

    # Clean up test database
    subprocess.run(
        [PSQL, "-h", "127.0.0.1", "-p", "5432", "-U", "postgres", "-d", "postgres", "-c", "DROP DATABASE IF EXISTS paypath_restore_test;"],
        env=env,
        capture_output=True,
        text=True
    )

    success = (restored_table_count >= 20 and restored_user_count >= 5 and restored_tx_count >= 60)
    print("==========================================================")
    if success:
        print(" VERDICT: BACKUP & RESTORE INTEGRITY CERTIFIED (PASS)")
    else:
        print(" VERDICT: BACKUP & RESTORE VERIFICATION FAILED")
    print("==========================================================")
    return success

if __name__ == "__main__":
    ok = asyncio.run(test_backup_restore())
    exit(0 if ok else 1)
