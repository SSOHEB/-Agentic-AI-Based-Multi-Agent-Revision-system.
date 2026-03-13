import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from backend.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from backend.models.user import User


class Topic(Base, TimestampMixin):
    """
    SQLAlchemy model representing the study topics table.
    """
    __tablename__ = "topics"

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
    
    title: Mapped[str] = mapped_column(
        String, 
        nullable=False
    )
    
    description: Mapped[str | None] = mapped_column(
        String, 
        nullable=True
    )
    
    difficulty_level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    # ── Scheduling columns ──────────────────────────
    current_interval_day: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    next_review_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    state: Mapped[str] = mapped_column(
        String,
        default="active",  # active | decaying | graduated
        nullable=False,
    )
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="topics")
