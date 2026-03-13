from uuid import UUID
from fastapi import HTTPException

from backend.models.question import Question
from backend.repositories.question_generation_repository import QuestionGenerationRepository
from backend.schemas.question_generation_schema import QuestionGenerationResponse


# Number of placeholder questions generated per topic
_QUESTIONS_PER_TOPIC = 2

# Difficulty distribution for generated questions
_DIFFICULTIES = ["L1", "L2"]


class QuestionGenerationService:
    """Orchestrates quiz question generation for a session.

    Currently generates placeholder questions.
    Will later integrate with RAG retrieval and the Quiz Agent
    for AI-based question generation.
    """

    def __init__(self, repository: QuestionGenerationRepository):
        self.repository = repository

    async def generate_questions_for_session(
        self, session_id: UUID
    ) -> QuestionGenerationResponse:
        """Generate questions for all topics attached to a session.

        Pipeline:
            1. Fetch topics linked to the session
            2. Generate placeholder questions (2 per topic)
            3. Store questions in the database
            4. Return summary
        """
        # 1 — Fetch session topics
        topics = await self.repository.get_session_topics(session_id)

        if not topics:
            raise HTTPException(
                status_code=404,
                detail="No topics found for this session",
            )

        # 2 — Generate placeholder questions
        questions = []
        for topic in topics:
            for i in range(_QUESTIONS_PER_TOPIC):
                difficulty = _DIFFICULTIES[i % len(_DIFFICULTIES)]
                question = Question(
                    quiz_session_id=session_id,
                    question_text=f"Placeholder question {i + 1} for topic: {topic.title}",
                    question_type="mcq",
                    difficulty=difficulty,
                    options={
                        "A": "Option A",
                        "B": "Option B",
                        "C": "Option C",
                        "D": "Option D",
                    },
                    correct_answer="A",
                )
                questions.append(question)

        # 3 — Store questions
        await self.repository.create_questions(session_id, questions)

        # 4 — Return summary
        return QuestionGenerationResponse(
            session_id=session_id,
            questions_created=len(questions),
        )
