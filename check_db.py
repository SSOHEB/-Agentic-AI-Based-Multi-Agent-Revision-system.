import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from backend.core.database import engine
from sqlalchemy import text

async def check():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT count(*) FROM answers"))
        print(f"Answers count: {result.scalar()}")

if __name__ == "__main__":
    asyncio.run(check())
