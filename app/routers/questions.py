from fastapi import APIRouter

from app.db.session import DbSession
from app.models.question_request import QuestionRequest
from app.services.retrieval import retrieve_vector

router = APIRouter(prefix = "/questions", tags=["questions"])

@router.post("/")
async def ask_question(request: QuestionRequest, db: DbSession):
    return retrieve_vector(db, request.question)