"""
Throwaway connectivity check -- run this ONCE after pasting your real
DATABASE_URL into backend/.env to confirm the app can reach Neon.

Run from the project root (areca-agent/) with:
    python -m backend.scripts.check_db_connection

Delete this file after a successful check (or leave it -- it's harmless).
"""

import sys
from sqlalchemy import text

# Import the engine (which loads DATABASE_URL via config.py -> backend/.env)
try:
    from backend.db.session import engine
except Exception as e:
    print(f"\n[FAIL]  Failed to import engine -- check that backend/.env exists and "
          f"DATABASE_URL is set:\n    {e}\n")
    sys.exit(1)

print("\n[...]  Attempting connection to Neon database ...")

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 AS ping"))
        row = result.fetchone()
        assert row[0] == 1, "Unexpected result from SELECT 1"
    print("[OK]   Connected successfully -- SELECT 1 returned 1.")
    print("       Your backend is wired to the Neon database correctly.\n")
except Exception as e:
    print(f"\n[FAIL]  Connection failed:\n    {e}\n")
    print("    Check that:\n"
          "      1. backend/.env contains a valid DATABASE_URL\n"
          "      2. The URL includes ?sslmode=require\n"
          "      3. Your IP is not blocked by Neon's connection limits\n")
    sys.exit(1)
