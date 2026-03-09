from backend.repositories.answer_repository import AnswerRepository
from backend.schemas.answer_schema import AnswerSubmitRequest
from backend.models.answer import Answer

class AnswerService:
    def __init__(self, repository: AnswerRepository):
        self.repository = repository

    async def submit_answer(self, data: AnswerSubmitRequest) -> Answer:
        answer = Answer(
            session_id=data.session_id,
            question_id=data.question_id,
            answer_text=data.answer_text
        )
        return await self.repository.create(answer)
