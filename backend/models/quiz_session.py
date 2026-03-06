import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from backend.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from backend.models.user import User


class QuizSession(Base, TimestampMixin):
    """
    SQLAlchemy model representing the quiz_sessions table.
    """
    __tablename__ = "quiz_sessions"

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
    
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )
    
    difficulty_level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )
    
    status: Mapped[str] = mapped_column(
        String,
        default="active", # e.g., "active", "completed", "abandoned"
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="quiz_sessions")
