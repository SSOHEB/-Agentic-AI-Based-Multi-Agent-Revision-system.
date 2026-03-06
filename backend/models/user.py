import uuid
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.models.topic import Topic
    from backend.models.quiz_session import QuizSession

from backend.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """
    SQLAlchemy model representing the users table.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    email: Mapped[str] = mapped_column(
        String, 
        unique=True, 
        index=True, 
        nullable=False
    )
    
    name: Mapped[str] = mapped_column(
        String, 
        nullable=False
    )
    
    firebase_uid: Mapped[str] = mapped_column(
        String, 
        unique=True, 
        nullable=False
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        nullable=False
    )

    # Relationships
    topics: Mapped[list["Topic"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    
    quiz_sessions: Mapped[list["QuizSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
