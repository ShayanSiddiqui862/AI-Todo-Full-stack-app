import asyncio
import os
import sys

# Add the backend directory to sys.path so we can import from it
backend_dir = os.path.join(os.getcwd(), 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import text
from db import async_engine

async def verify_columns():
    print("Verifying database columns...")
    async with async_engine.begin() as conn:
        # Check if the new columns exist
        result = await conn.execute(text("SELECT priority, tags, recurrence_type FROM task LIMIT 1"))
        print("Successfully queried new columns.")
        # We don't need to fetch result, just execution without error is enough proof of schema existence

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(verify_columns())
        print("Verification successful!")
    except Exception as e:
        print(f"Verification failed: {e}")
        sys.exit(1)
