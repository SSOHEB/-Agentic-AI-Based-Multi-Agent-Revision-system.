from pydantic import BaseModel
from uuid import UUID


class SessionCompleteResponse(BaseModel):
    session_id: UUID
    status: str
