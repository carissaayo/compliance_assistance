from pydantic import BaseModel

from app.models.chunk_response import ChunkResponse


class AnswerResponse(BaseModel):
    answer: str
    grounded: bool
    sources: list[ChunkResponse]
