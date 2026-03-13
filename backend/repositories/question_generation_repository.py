from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.topic import Topic
from backend.models.question import Question
from backend.models.session_topic import SessionTopic


class QuestionGenerationRepository:
    """Repository for question generation database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_session_topics(self, session_id: UUID) -> List[Topic]:
        """Return topics linked to a session via the session_topics junction table."""
        stmt = (
            select(Topic)
            .join(SessionTopic, SessionTopic.topic_id == Topic.id)
            .where(SessionTopic.session_id == session_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_questions(
        self, session_id: UUID, questions: List[Question]
    ) -> List[Question]:
        """Bulk-insert generated questions for a session."""
        for question in questions:
            question.quiz_session_id = session_id
            self.session.add(question)
        await self.session.commit()
        return questions
