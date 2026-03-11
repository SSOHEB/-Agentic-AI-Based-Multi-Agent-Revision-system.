import asyncio
import uuid
import sys
import os

from fastapi.testclient import TestClient
from backend.main import app

sys.path.insert(0, os.path.dirname(__file__))
from backend.core.database import engine
from backend.models import Base
from backend.models.question import Question

async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def test_get_questions():
    client = TestClient(app)
    
    # We use a random UUID. This should either return 404 (because session doesn't exist)
    # or 200 [] (if session exists). Because we check session existence:
    
    session_id = str(uuid.uuid4())
    response = client.get(f"/quiz/{session_id}/questions")
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")

if __name__ == "__main__":
    asyncio.run(setup_db())
    test_get_questions()
