from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from backend.core.dependencies import get_db
from backend.repositories.progress_repository import ProgressRepository
from backend.services.progress_service import ProgressService
from backend.schemas.progress_schema import DashboardResponse


router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    user_id: UUID = Query(..., description="The user's UUID"),
    db: AsyncSession = Depends(get_db),
):
    repository = ProgressRepository(db)
    service = ProgressService(repository)
    return await service.get_dashboard_metrics(user_id)
