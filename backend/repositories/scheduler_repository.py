from typing import List
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.topic import Topic
from backend.models.quiz_session import QuizSession
from backend.models.session_topic import SessionTopic


class SchedulerRepository:
    """Repository for scheduler-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_due_topics(self, user_id: UUID) -> List[Topic]:
        """Return topics whose next_review_date has passed (or is NULL)."""
        now = datetime.now(timezone.utc)
        stmt = (
            select(Topic)
            .where(
                Topic.user_id == user_id,
                Topic.state != "graduated",
                (Topic.next_review_date <= now) | (Topic.next_review_date.is_(None)),
            )
            .order_by(Topic.next_review_date.asc().nullsfirst())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_quiz_session(self, user_id: UUID) -> QuizSession:
        """Create a pre-generated quiz session for the scheduler."""
        session = QuizSession(
            user_id=user_id,
            topic_id=None,  # multi-topic sessions use session_topics instead
            status="pre_generated",
            started_at=datetime.now(timezone.utc),
        )
        self.session.add(session)
        await self.session.commit()
        await self.session.refresh(session)
        return session

    async def attach_topics_to_session(
        self, session_id: UUID, topic_ids: List[UUID]
    ) -> None:
        """Link topics to a quiz session via the junction table."""
        for topic_id in topic_ids:
            link = SessionTopic(session_id=session_id, topic_id=topic_id)
            self.session.add(link)
        await self.session.commit()
