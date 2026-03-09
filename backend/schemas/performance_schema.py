from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class PerformanceLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    topic_id: UUID
    session_id: UUID
    performance_score: float
    retention_before: Optional[float] = None
    retention_after: Optional[float] = None
    logged_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
