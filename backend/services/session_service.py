from uuid import UUID
from fastapi import HTTPException

from backend.repositories.session_repository import SessionRepository
from backend.services.performance_service import PerformanceService
from backend.schemas.session_schema import SessionCompleteResponse


class SessionService:
    """Orchestrates quiz-session lifecycle operations.

    Dependencies:
        session_repository  – DB access for quiz_sessions
        performance_service – computes & logs session performance
    """

    def __init__(
        self,
        session_repository: SessionRepository,
        performance_service: PerformanceService,
    ):
        self.session_repository = session_repository
        self.performance_service = performance_service

    async def complete_session(self, session_id: UUID) -> SessionCompleteResponse:
        """Finalize a quiz session.

        Pipeline:
            1. Validate session exists
            2. Prevent double completion
            3. Log performance via PerformanceService
            4. Mark session as completed
            5. Return completion summary
        """
        # 1 — Validate session exists
        session = await self.session_repository.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Quiz session not found")

        # 2 — Prevent double completion
        if session.status == "completed":
            raise HTTPException(
                status_code=400,
                detail="Session is already completed",
            )

        # 3 — Compute and log performance
        await self.performance_service.log_session_performance(session_id)

        # 4 — Mark session completed
        await self.session_repository.update_session_status(session_id, "completed")

        # 5 — Return summary
        # Note: Retention recalculation is handled later by the Progress layer
        return SessionCompleteResponse(
            session_id=session_id,
            status="completed",
        )
