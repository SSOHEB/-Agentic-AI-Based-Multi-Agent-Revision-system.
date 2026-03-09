from datetime import datetime, timezone
from backend.models.quiz_session import QuizSession
from backend.repositories.session_repository import SessionRepository
from backend.schemas.quiz_schema import QuizStartRequest

from backend.repositories.question_repository import QuestionRepository
from backend.repositories.answer_repository import AnswerRepository
from backend.models.question import Question
from backend.schemas.quiz_schema import QuizResultResponse
from fastapi import HTTPException
from typing import List
from uuid import UUID

class QuizService:
    def __init__(self, repository: SessionRepository, question_repository: QuestionRepository = None, answer_repository: AnswerRepository = None):
        self.repository = repository
        self.question_repository = question_repository
        self.answer_repository = answer_repository

    async def start_quiz(self, data: QuizStartRequest) -> QuizSession:
        new_session = QuizSession(
            user_id=data.user_id,
            topic_id=data.topic_id,
            status="started",
            started_at=datetime.now(timezone.utc)
        )
        return await self.repository.create(new_session)

    async def get_questions_for_session(self, session_id: UUID) -> List[Question]:
        session = await self.repository.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Quiz session not found")
        
        return await self.question_repository.get_questions_by_session(session_id)

    async def compute_quiz_results(self, session_id: UUID) -> QuizResultResponse:
        session = await self.repository.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Quiz session not found")
            
        questions = await self.question_repository.get_questions_by_session(session_id)
        if not questions:
            return QuizResultResponse(
                session_id=session_id,
                total_questions=0,
                correct_answers=0,
                accuracy_percent=0.0
            )
            
        answers = await self.answer_repository.get_session_answers(session_id)
        
        # Build dictionary for O(1) lookups
        answers_by_question = {str(a.question_id): a.answer_text for a in answers}
        
        correct_count = 0
        for q in questions:
            student_answer = answers_by_question.get(str(q.id))
            if student_answer and student_answer.strip().lower() == q.correct_answer.strip().lower():
                correct_count += 1
                
        accuracy = (correct_count / len(questions)) * 100
        
        # Optionally, save score to session
        session.score = accuracy
        await self.repository.session.commit()
        
        return QuizResultResponse(
            session_id=session_id,
            total_questions=len(questions),
            correct_answers=correct_count,
            accuracy_percent=accuracy
        )
