from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.repositories.answer_repository import AnswerRepository
from backend.services.answer_service import AnswerService
from backend.schemas.answer_schema import AnswerSubmitRequest, AnswerResponse

router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"]
)

@router.post("/answer", response_model=AnswerResponse)
async def submit_answer(
    request: AnswerSubmitRequest,
    db: AsyncSession = Depends(get_db)
):
    repository = AnswerRepository(db)
    service = AnswerService(repository)
    return await service.submit_answer(request)
