from sqlalchemy import select

from app.db.session import DbSession
from app.models.chunk import Chunk
from app.models.chunk_response import ChunkResponse
from app.services.embedding.factory import get_embedding_provider


def retrieve_vector(db: DbSession, question: str):
    provider = get_embedding_provider()
    query_vector = provider.embed([question])[0]

    distance = Chunk.embedding.cosine_distance(query_vector).label("distance")
    stmt = select(Chunk,distance).order_by(distance).limit(5)

    chunks = db.execute(stmt).scalars().all()


    return [
        ChunkResponse(
            content=chunk.content,
            page_reference=chunk.page_reference,
            position=chunk.position,
            score= score,
        )
        for chunk, score in chunks
    ]