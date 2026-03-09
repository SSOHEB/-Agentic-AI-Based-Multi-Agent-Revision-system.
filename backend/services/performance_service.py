from uuid import UUID
from fastapi import HTTPException
from datetime import datetime, timezone

from backend.repositories.performance_repository import PerformanceRepository
from backend.repositories.session_repository import SessionRepository
from backend.repositories.question_repository import QuestionRepository
from backend.repositories.answer_repository import AnswerRepository
from backend.models.performance_log import PerformanceLog
from backend.schemas.performance_schema import PerformanceLogResponse

class PerformanceService:
    def __init__(self, 
                 repository: PerformanceRepository, 
                 session_repository: SessionRepository,
                 question_repository: QuestionRepository,
                 answer_repository: AnswerRepository):
        self.repository = repository
        self.session_repository = session_repository
        self.question_repository = question_repository
        self.answer_repository = answer_repository

    async def log_session_performance(self, session_id: UUID) -> PerformanceLogResponse:
        session = await self.session_repository.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Quiz session not found")
            
        questions = await self.question_repository.get_questions_by_session(session_id)
        if not questions:
            raise HTTPException(status_code=400, detail="Cannot log performance for empty quiz session")
            
        answers = await self.answer_repository.get_session_answers(session_id)
        
        # Calculate correct answers
        answers_by_question = {str(a.question_id): a.answer_text for a in answers}
        
        correct_count = 0
        for q in questions:
            student_answer = answers_by_question.get(str(q.id))
            if student_answer and student_answer.strip().lower() == q.correct_answer.strip().lower():
                correct_count += 1
                
        performance_score = correct_count / len(questions)
        
        # Here we check if there's any previous logic to calculate retention
        # We leave space for the formulas to be implemented cleanly later in core/retention.py
        # For now, it records the performance mapping strictly.
        
        log = PerformanceLog(
            user_id=session.user_id,
            topic_id=session.topic_id,
            session_id=session.id,
            performance_score=performance_score,
            retention_before=None, # To be added later via core/retention.py
            retention_after=None,  # To be added later via core/retention.py
            logged_at=datetime.now(timezone.utc)
        )
        
        stored_log = await self.repository.create_log(log)
        
        return PerformanceLogResponse.model_validate(stored_log)
