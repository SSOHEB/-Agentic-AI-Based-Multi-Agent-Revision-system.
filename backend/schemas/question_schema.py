from pydantic import BaseModel, ConfigDict
from typing import Dict, Any
from uuid import UUID

class QuestionResponse(BaseModel):
    id: UUID
    question_text: str
    question_type: str
    difficulty: str
    options: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)
