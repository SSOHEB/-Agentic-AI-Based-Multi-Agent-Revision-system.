import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from backend.models.base import Base


class SessionTopic(Base):
    """
    Junction table linking quiz_sessions to topics.

    Allows a single quiz session to cover multiple topics,
    which is required for the scheduler's batching and
    merging algorithm.
    """
    __tablename__ = "session_topics"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quiz_sessions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", ondelete="CASCADE"),
        primary_key=True,
    )
