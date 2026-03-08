from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.dependencies import get_db
from backend.repositories.topic_repository import TopicRepository
from backend.schemas.topic_schema import TopicCreate, TopicResponse
from backend.services.topic_service import TopicService

router = APIRouter(
    prefix="/topics",
    tags=["Topics"]
)

@router.post("/", response_model=TopicResponse)
async def create_topic(
    topic_data: TopicCreate,
    db: AsyncSession = Depends(get_db)
):
    repository = TopicRepository(db)
    service = TopicService(repository)
    return await service.create_topic(topic_data)

@router.get("/user/{user_id}", response_model=List[TopicResponse])
async def get_user_topics(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    repository = TopicRepository(db)
    service = TopicService(repository)
    return await service.get_user_topics(user_id)
