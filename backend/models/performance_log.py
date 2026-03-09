import uuid
from sqlalchemy import Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone

from backend.models.base import Base

class PerformanceLog(Base):
    __tablename__ = "performance_log"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    topic_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quiz_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    performance_score: Mapped[float] = mapped_column(Float, nullable=False)
    
    retention_before: Mapped[float | None] = mapped_column(Float, nullable=True)
    retention_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
