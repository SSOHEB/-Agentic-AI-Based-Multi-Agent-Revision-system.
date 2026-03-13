from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from backend.core.dependencies import get_db
from backend.repositories.question_generation_repository import QuestionGenerationRepository
from backend.services.question_generation_service import QuestionGenerationService
from backend.schemas.question_generation_schema import QuestionGenerationResponse


router = APIRouter(prefix="/quiz", tags=["Quiz Generation"])


@router.post("/{session_id}/generate", response_model=QuestionGenerationResponse)
async def generate_questions(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    repository = QuestionGenerationRepository(db)
    service = QuestionGenerationService(repository)
    return await service.generate_questions_for_session(session_id)
