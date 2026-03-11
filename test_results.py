import asyncio
import uuid
import sys
import os

from fastapi.testclient import TestClient
from backend.main import app

sys.path.insert(0, os.path.dirname(__file__))
from backend.core.database import engine
from backend.models import Base

async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def test_get_results():
    client = TestClient(app)
    
    session_id = str(uuid.uuid4())
    # Should be 404 because session does not exist
    response = client.get(f"/quiz/{session_id}/results")
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")

if __name__ == "__main__":
    asyncio.run(setup_db())
    test_get_results()
