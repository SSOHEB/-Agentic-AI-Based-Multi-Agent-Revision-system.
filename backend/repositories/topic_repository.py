from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.topic import Topic


class TopicRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, topic: Topic) -> Topic:
        self.session.add(topic)
        await self.session.commit()
        await self.session.refresh(topic)
        return topic

    async def get_user_topics(self, user_id: UUID) -> List[Topic]:
        stmt = select(Topic).where(Topic.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
