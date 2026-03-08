from datetime import datetime, timezone
from backend.models.quiz_session import QuizSession
from backend.repositories.session_repository import SessionRepository
from backend.schemas.quiz_schema import QuizStartRequest

class QuizService:
    def __init__(self, repository: SessionRepository):
        self.repository = repository

    async def start_quiz(self, data: QuizStartRequest) -> QuizSession:
        new_session = QuizSession(
            user_id=data.user_id,
            topic_id=data.topic_id,
            status="started",
            started_at=datetime.now(timezone.utc)
        )
        return await self.repository.create(new_session)
