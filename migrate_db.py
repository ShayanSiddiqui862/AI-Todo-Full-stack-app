import asyncio
import os
import sys

# Add the backend directory to sys.path so we can import from it
backend_dir = os.path.join(os.getcwd(), 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import text
from db import async_engine

async def migrate():
    print("Starting database migration...")
    async with async_engine.begin() as conn:
        print("Checking for missing columns in 'task' table...")
        
        # List of columns to check and adding them if missing
        # Format: (column_name, data_type, default_value)
        columns_to_add = [
            ("priority", "VARCHAR(10)", "DEFAULT 'medium'"),
            ("tags", "VARCHAR[]", "NULL"),
            ("due_date", "TIMESTAMP", "NULL"),
            ("remind_at", "TIMESTAMP", "NULL"),
            ("recurrence_type", "VARCHAR(20)", "DEFAULT 'none'"),
            ("recurrence_interval", "INTEGER", "DEFAULT 1")
        ]

        for col_name, data_type, default_val in columns_to_add:
            try:
                # Check if column exists
                check_sql = text(f"SELECT 1 FROM information_schema.columns WHERE table_name='task' AND column_name='{col_name}'")
                result = await conn.execute(check_sql)
                if result.scalar():
                    print(f"Column '{col_name}' already exists.")
                else:
                    print(f"Adding column '{col_name}'...")
                    alter_sql = text(f"ALTER TABLE task ADD COLUMN {col_name} {data_type} {default_val}")
                    await conn.execute(alter_sql)
                    print(f"Column '{col_name}' added successfully.")
            except Exception as e:
                print(f"Error checking/adding column '{col_name}': {e}")
                
    print("Migration completed.")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(migrate())
