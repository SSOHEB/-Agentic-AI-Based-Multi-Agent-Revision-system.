from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class TopicCreate(BaseModel):
    title: str
    description: Optional[str] = None
    difficulty_level: Optional[int] = None
    user_id: UUID

class TopicResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    difficulty_level: Optional[int] = None
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)
