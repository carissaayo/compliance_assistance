from fastapi import APIRouter

from app.db.session import DbSession
from app.models.question_request import QuestionRequest
from app.services.generation import generate_answer
from app.services.retrieval import retrieve_keyword, retrieve_vector

router = APIRouter(prefix = "/questions", tags=["questions"])

@router.post("/")
async def ask_question(request: QuestionRequest, db: DbSession):
    return generate_answer(db, request.question)



@router.post("/retrieve")
async def retrieve_only(request: QuestionRequest, db: DbSession):
    return retrieve_vector(db, request.question)


@router.post("/keyword")
async def keyword_only(request: QuestionRequest, db: DbSession):
 

    return retrieve_keyword(db, request.question)