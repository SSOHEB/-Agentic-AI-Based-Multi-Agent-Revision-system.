from uuid import UUID

from backend.repositories.scheduler_repository import SchedulerRepository
from backend.schemas.scheduler_schema import SchedulerResponse


# Maximum number of topics per generated session
_MAX_TOPICS_PER_SESSION = 5


class SchedulerService:
    """Orchestrates quiz session generation based on spaced-repetition schedule.

    This module will later integrate with the retention engine and
    difficulty thresholds.
    """

    def __init__(self, repository: SchedulerRepository):
        self.repository = repository

    async def schedule_next_session(self, user_id: UUID) -> SchedulerResponse:
        """Generate a new quiz session for topics that are due for review.

        Pipeline:
            1. Fetch due topics
            2. If none due → return no_topics_due
            3. Cap at _MAX_TOPICS_PER_SESSION
            4. Create one quiz session
            5. Attach selected topics via session_topics
            6. Return summary
        """
        # 1 — Fetch due topics
        topics = await self.repository.get_due_topics(user_id)

        # 2 — Nothing due
        if not topics:
            return SchedulerResponse(
                session_id=None,
                topics_count=0,
                status="no_topics_due",
            )

        # 3 — Cap session size
        session_topics = topics[:_MAX_TOPICS_PER_SESSION]
        topic_ids = [t.id for t in session_topics]

        # 4 — Create quiz session
        session = await self.repository.create_quiz_session(user_id)

        # 5 — Attach topics
        await self.repository.attach_topics_to_session(session.id, topic_ids)

        # 6 — Return summary
        return SchedulerResponse(
            session_id=session.id,
            topics_count=len(topic_ids),
            status="created",
        )
