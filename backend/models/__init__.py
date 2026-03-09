# Backend Models Package Initialization
# 
# We explicitly import and expose all SQLAlchemy ORM models here.
# This ensures that when Alembic (our migration tool) imports the models package,
# it automatically discovers all of these classes and includes them when auto-generating migrations.

from backend.models.base import Base
from backend.models.user import User
from backend.models.topic import Topic
from backend.models.quiz_session import QuizSession
from backend.models.answer import Answer

# Define the models exposed by this package
__all__ = [
    "Base",
    "User",
    "Topic",
    "QuizSession",
    "Answer"
]
