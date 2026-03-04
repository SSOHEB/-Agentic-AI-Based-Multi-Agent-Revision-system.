import pytest
from httpx import AsyncClient, ASGITransport

from main import app

@pytest.mark.asyncio
async def test_health_check():
    """
    Test the root health check endpoint to ensure the API is running operations.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/")
    
    # Assert successful status code
    assert response.status_code == 200
    
    # Assert expected JSON body structure
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "smart-revision-backend"
