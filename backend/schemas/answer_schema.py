from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class AnswerSubmitRequest(BaseModel):
    session_id: UUID
    question_id: UUID
    answer_text: str

class AnswerResponse(BaseModel):
    id: UUID
    session_id: UUID
    question_id: UUID
    answer_text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
