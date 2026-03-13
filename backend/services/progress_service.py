from uuid import UUID
from datetime import datetime, timezone

from backend.repositories.progress_repository import ProgressRepository
from backend.schemas.progress_schema import DashboardResponse
from backend.core.retention import compute_system_retention


# Default interval-day schedule used when deriving topic state
_INTERVAL_SCHEDULE = [1, 3, 7, 21, 60]


class ProgressService:
    """Orchestrates dashboard analytics calculations.

    All retention math is delegated to core.retention (pure Python, no DB).
    """

    def __init__(self, repository: ProgressRepository):
        self.repository = repository

    async def get_dashboard_metrics(self, user_id: UUID) -> DashboardResponse:
        """Build the full progress dashboard for a user.

        Steps:
            1. Fetch topics & latest performance per topic
            2. Build topic dicts for compute_system_retention
            3. Call compute_system_retention
            4. Compute exam readiness
            5. Return DashboardResponse
        """
        # 1 — Fetch data
        topics = await self.repository.get_user_topics(user_id)
        latest_logs = await self.repository.get_latest_performance_per_topic(user_id)
        recent_scores = await self.repository.get_recent_l3_scores(user_id)
        graduated_count = await self.repository.get_graduated_topic_count(user_id)

        topics_total = len(topics)

        # 2 — Build topic dicts expected by compute_system_retention
        now = datetime.now(timezone.utc)
        log_by_topic = {str(log.topic_id): log for log in latest_logs}

        topic_dicts = []
        for topic in topics:
            log = log_by_topic.get(str(topic.id))
            if not log:
                continue  # no performance data yet — skip

            days_since = (now - log.logged_at).days

            topic_dicts.append({
                "latest_performance_score": log.performance_score,
                "days_since_last_session": days_since,
                "current_interval_day": topic.current_interval_day,
                "state": topic.state,
            })

        # 3 — System retention via core.retention
        retention_result = compute_system_retention(topic_dicts)

        # 4 — Exam readiness
        # coverage = proportion of syllabus topics the user has graduated
        # TODO: replace topics_total with total syllabus topics from document_chunks
        coverage_score = (
            graduated_count / topics_total if topics_total > 0 else 0.0
        )
        avg_l3_score = (
            sum(s.performance_score for s in recent_scores) / len(recent_scores)
            if recent_scores
            else 0.0
        )
        retention_meter = retention_result["retention_percent"] / 100.0

        readiness = (
            coverage_score * 0.50
            + avg_l3_score * 0.30
            + retention_meter * 0.20
        )
        exam_readiness = int(round(readiness * 100))

        # 5 — Return
        return DashboardResponse(
            retention_percent=retention_result["retention_percent"],
            trend=retention_result["trend"],
            exam_readiness=exam_readiness,
            topics_total=topics_total,
            topics_graduated=graduated_count,
        )
