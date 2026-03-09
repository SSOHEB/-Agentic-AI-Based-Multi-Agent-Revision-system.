from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.dependencies import get_db
from backend.repositories.session_repository import SessionRepository
from backend.schemas.quiz_schema import QuizStartRequest, QuizSessionResponse
from backend.schemas.question_schema import QuestionResponse
from backend.services.quiz_service import QuizService
from backend.repositories.question_repository import QuestionRepository
from typing import List
from uuid import UUID

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

@router.get("/{session_id}/questions", response_model=List[QuestionResponse])
async def get_questions_for_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    session_repo = SessionRepository(db)
    question_repo = QuestionRepository(db)
    service = QuizService(session_repo, question_repo)
    return await service.get_questions_for_session(session_id)
