from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional

from backend.models.performance_log import PerformanceLog

class PerformanceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_log(self, performance_log: PerformanceLog) -> PerformanceLog:
        self.session.add(performance_log)
        await self.session.commit()
        await self.session.refresh(performance_log)
        return performance_log

    async def get_latest_topic_performance(self, topic_id: UUID) -> Optional[PerformanceLog]:
        stmt = select(PerformanceLog).where(
            PerformanceLog.topic_id == topic_id
        ).order_by(PerformanceLog.logged_at.desc()).limit(1)
        
        result = await self.session.execute(stmt)
        return result.scalars().first()
