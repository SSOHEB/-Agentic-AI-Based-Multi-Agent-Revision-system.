import asyncio
from fastapi.testclient import TestClient
from backend.main import app
import uuid

def test_submit_answer():
    client = TestClient(app)
    
    # We use random UUIDs for session_id and question_id.
    # If the DB doesn't exist or FK constraint fails, this will throw a 500 error
    # which we can catch to see if the backend logic works.
    # Otherwise it should return 200 OK.
    
    payload = {
        "session_id": str(uuid.uuid4()),
        "question_id": str(uuid.uuid4()),
        "answer_text": "Dynamic programming stores subproblem results."
    }
    
    response = client.post("/quiz/answer", json=payload)
    print("Response Status:", response.status_code)
    print("Response Body:", response.json())

if __name__ == "__main__":
    test_submit_answer()
