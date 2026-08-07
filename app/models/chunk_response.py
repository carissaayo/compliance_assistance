from pydantic import BaseModel


class ChunkResponse(BaseModel):
    content: str
    page_reference: int
    position: int
    score: float