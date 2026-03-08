from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.dependencies import get_db
from backend.repositories.session_repository import SessionRepository
from backend.schemas.quiz_schema import QuizStartRequest, QuizSessionResponse
from backend.services.quiz_service import QuizService

router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"]
)

@router.post("/start", response_model=QuizSessionResponse)
async def start_quiz(
    request_data: QuizStartRequest,
    db: AsyncSession = Depends(get_db)
):
    repository = SessionRepository(db)
    service = QuizService(repository)
    return await service.start_quiz(request_data)
