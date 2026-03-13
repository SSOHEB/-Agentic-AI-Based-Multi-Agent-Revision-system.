from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from backend.core.dependencies import get_db
from backend.repositories.scheduler_repository import SchedulerRepository
from backend.services.scheduler_service import SchedulerService
from backend.schemas.scheduler_schema import SchedulerResponse


router = APIRouter(prefix="/scheduler", tags=["Scheduler"])


@router.post("/generate", response_model=SchedulerResponse)
async def generate_session(
    user_id: UUID = Query(..., description="The user's UUID"),
    db: AsyncSession = Depends(get_db),
):
    repository = SchedulerRepository(db)
    service = SchedulerService(repository)
    return await service.schedule_next_session(user_id)
