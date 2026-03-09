from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.answer import Answer

class AnswerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, answer: Answer) -> Answer:
        self.session.add(answer)
        await self.session.commit()
        await self.session.refresh(answer)
        return answer

    async def get_session_answers(self, session_id: UUID) -> List[Answer]:
        stmt = select(Answer).where(Answer.session_id == session_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
