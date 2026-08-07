from pydantic import BaseModel


class ChunkResponse(BaseModel):
    content: str
    page_reference: str | None
    position: int
    score: float