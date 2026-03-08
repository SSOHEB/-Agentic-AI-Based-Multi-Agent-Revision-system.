from typing import List
from uuid import UUID

from backend.models.topic import Topic
from backend.repositories.topic_repository import TopicRepository
from backend.schemas.topic_schema import TopicCreate


class TopicService:
    def __init__(self, repository: TopicRepository):
        self.repository = repository

    async def create_topic(self, data: TopicCreate) -> Topic:
        difficulty = data.difficulty_level if data.difficulty_level is not None else 1
        new_topic = Topic(
            title=data.title,
            description=data.description,
            difficulty_level=difficulty,
            user_id=data.user_id
        )
        return await self.repository.create(new_topic)

    async def get_user_topics(self, user_id: UUID) -> List[Topic]:
        return await self.repository.get_user_topics(user_id)
