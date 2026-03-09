import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from backend.core.database import engine
from backend.models import Base
from backend.models.answer import Answer

async def create_tables():
    async with engine.begin() as conn:
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Done.")

if __name__ == "__main__":
    asyncio.run(create_tables())
