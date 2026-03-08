from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.quiz_session import QuizSession

class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, session: QuizSession) -> QuizSession:
        self.session.add(session)
        await self.session.commit()
        await self.session.refresh(session)
        return session

    async def get_session(self, session_id: UUID) -> QuizSession | None:
        stmt = select(QuizSession).where(QuizSession.id == session_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
