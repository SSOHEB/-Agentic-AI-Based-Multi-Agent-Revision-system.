from datetime import datetime, timezone
from backend.models.quiz_session import QuizSession
from backend.repositories.session_repository import SessionRepository
from backend.schemas.quiz_schema import QuizStartRequest

from backend.repositories.question_repository import QuestionRepository
from backend.models.question import Question
from fastapi import HTTPException
from typing import List
from uuid import UUID

class QuizService:
    def __init__(self, repository: SessionRepository, question_repository: QuestionRepository = None):
        self.repository = repository
        self.question_repository = question_repository

    async def start_quiz(self, data: QuizStartRequest) -> QuizSession:
        new_session = QuizSession(
            user_id=data.user_id,
            topic_id=data.topic_id,
            status="started",
            started_at=datetime.now(timezone.utc)
        )
        return await self.repository.create(new_session)

    async def get_questions_for_session(self, session_id: UUID) -> List[Question]:
        session = await self.repository.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Quiz session not found")
        
        return await self.question_repository.get_questions_by_session(session_id)
