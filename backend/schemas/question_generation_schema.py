from pydantic import BaseModel
from uuid import UUID


class QuestionGenerationResponse(BaseModel):
    session_id: UUID
    questions_created: int
