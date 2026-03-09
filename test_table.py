import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from backend.core.database import engine
from backend.models import Base
from backend.models.answer import Answer
from sqlalchemy import text

async def main():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT count(*) FROM answers"))
            count = result.scalar()
        
        with open("db_result.txt", "w") as f:
            f.write(f"SUCCESS: Answers table exists. Count: {count}")
    except Exception as e:
        with open("db_result.txt", "w") as f:
            f.write(f"ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
