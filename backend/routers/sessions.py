from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from backend.core.dependencies import get_db
from backend.repositories.session_repository import SessionRepository
from backend.repositories.performance_repository import PerformanceRepository
from backend.repositories.question_repository import QuestionRepository
from backend.repositories.answer_repository import AnswerRepository
from backend.services.performance_service import PerformanceService
from backend.services.session_service import SessionService
from backend.schemas.session_schema import SessionCompleteResponse


router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("/{session_id}/complete", response_model=SessionCompleteResponse)
async def complete_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    # Build repositories
    session_repo = SessionRepository(db)
    performance_repo = PerformanceRepository(db)
    question_repo = QuestionRepository(db)
    answer_repo = AnswerRepository(db)

    # Build services (PerformanceService owns the sub-repos)
    performance_service = PerformanceService(
        repository=performance_repo,
        session_repository=session_repo,
        question_repository=question_repo,
        answer_repository=answer_repo,
    )

    service = SessionService(
        session_repository=session_repo,
        performance_service=performance_service,
    )

    return await service.complete_session(session_id)
