from fastapi import APIRouter

from app.db.session import DbSession
from app.models.question_request import QuestionRequest
from app.services.generation import generate_answer

router = APIRouter(prefix = "/questions", tags=["questions"])

@router.post("/")
async def ask_question(request: QuestionRequest, db: DbSession):
    return generate_answer(db, request.question)