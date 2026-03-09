from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.question import Question

class QuestionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_questions_by_session(self, session_id: UUID) -> List[Question]:
        stmt = select(Question).where(Question.quiz_session_id == session_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
