from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.topic import Topic
from backend.models.performance_log import PerformanceLog


class ProgressRepository:
    """Read-only repository for progress analytics queries."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_topics(self, user_id: UUID) -> List[Topic]:
        """Return all topics belonging to a user."""
        stmt = select(Topic).where(Topic.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_l3_scores(self, user_id: UUID) -> List[PerformanceLog]:
        """Return the latest performance logs for a user (most recent first).

        'L3' refers to the third spaced-repetition interval (day 7),
        but this returns all recent logs so the service can filter as needed.
        """
        stmt = (
            select(PerformanceLog)
            .where(PerformanceLog.user_id == user_id)
            .order_by(PerformanceLog.logged_at.desc())
            .limit(50)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_graduated_topic_count(self, user_id: UUID) -> int:
        """Count topics that have reached 'graduated' state.

        Since the Topic model does not yet have a `state` column,
        we approximate graduation by checking if the topic has at least
        5 performance logs with an average score >= 0.85.
        """
        # Subquery: topic_ids with >= 5 logs and avg score >= 0.85
        subq = (
            select(PerformanceLog.topic_id)
            .where(PerformanceLog.user_id == user_id)
            .group_by(PerformanceLog.topic_id)
            .having(
                func.count(PerformanceLog.id) >= 5,
                func.avg(PerformanceLog.performance_score) >= 0.85,
            )
        ).subquery()

        stmt = select(func.count()).select_from(subq)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_latest_performance_per_topic(
        self, user_id: UUID
    ) -> List[PerformanceLog]:
        """Return the most recent PerformanceLog for each of the user's topics."""
        # Subquery: max logged_at per topic
        latest_sub = (
            select(
                PerformanceLog.topic_id,
                func.max(PerformanceLog.logged_at).label("max_logged"),
            )
            .where(PerformanceLog.user_id == user_id)
            .group_by(PerformanceLog.topic_id)
        ).subquery()

        stmt = (
            select(PerformanceLog)
            .join(
                latest_sub,
                (PerformanceLog.topic_id == latest_sub.c.topic_id)
                & (PerformanceLog.logged_at == latest_sub.c.max_logged),
            )
            .where(PerformanceLog.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
