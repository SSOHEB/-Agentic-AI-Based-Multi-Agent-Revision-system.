from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class SchedulerResponse(BaseModel):
    session_id: Optional[UUID] = None
    topics_count: int
    status: str  # "created" | "no_topics_due"
