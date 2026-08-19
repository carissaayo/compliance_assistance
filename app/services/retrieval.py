from sqlalchemy import func, select

from app.config import settings
from app.db.session import DbSession
from app.models.chunk import Chunk
from app.models.chunk_response import ChunkResponse
from app.services.embedding.factory import get_embedding_provider


def retrieve_vector(db: DbSession, question: str, top_k: int = 5):
    provider = get_embedding_provider()
    query_vector = provider.embed([question])[0]

    distance = Chunk.embedding.cosine_distance(query_vector).label("distance")
    stmt = (
        select(Chunk, distance).where(Chunk.embedding.is_not(None)).order_by(distance).limit(top_k)
    )
    rows = db.execute(stmt).all() 



    return [
        ChunkResponse(
            content=chunk.content,
            page_reference=chunk.page_reference,
            position=chunk.position,
            score= float(dist),
        )
        for chunk, dist in rows
    ]


def retrieve_keyword(db: DbSession, question: str, top_k: int = 20) -> list[ChunkResponse]:
    tsquery = func.plainto_tsquery("english", question)
    rank = func.ts_rank(Chunk.search_vector, tsquery).label("rank")
    stmt = (
        select(Chunk, rank)
        .where(Chunk.search_vector.is_not(None))
        .where(Chunk.search_vector.op("@@")(tsquery))
        .order_by(rank.desc())
        .limit(top_k)
    )
    rows = db.execute(stmt).all()
    return [
        ChunkResponse(
            content=chunk.content,
            page_reference=chunk.page_reference,
            position=chunk.position,
            score=float(rank_score),
        )
        for chunk, rank_score in rows
    ]



def retrieve_hybrid(
    db: DbSession,
    question: str,
    top_k: int = 5,
) -> list[ChunkResponse]:
    vector_hits = retrieve_vector(db, question, top_k=20)
    keyword_hits = retrieve_keyword(db, question, top_k=20)

    # index by position so we can merge on a stable key
    seen: dict[int, ChunkResponse] = {}

    # vector score = cosine distance (lower = better), normalise to 0-1 similarity
    for chunk in vector_hits:
        if chunk.score > settings.retrieval_max_distance: 
            continue
        similarity = 1.0 - chunk.score  # flip: higher is now better
        seen[chunk.position] = ChunkResponse(
            content=chunk.content,
            page_reference=chunk.page_reference,
            position=chunk.position,
            score=similarity,
        )

    # keyword rank is already higher=better, normalise by dividing by max
    max_keyword = max((c.score for c in keyword_hits), default=1.0) or 1.0
    for chunk in keyword_hits:
        normalised = chunk.score / max_keyword
        if chunk.position in seen:
            # boost existing entry
            seen[chunk.position] = ChunkResponse(
                content=seen[chunk.position].content,
                page_reference=seen[chunk.position].page_reference,
                position=chunk.position,
                score=seen[chunk.position].score + normalised,
            )
        else:
            seen[chunk.position] = ChunkResponse(
                content=chunk.content,
                page_reference=chunk.page_reference,
                position=chunk.position,
                score=normalised,
            )

    merged = sorted(seen.values(), key=lambda c: c.score, reverse=True)
    return merged[:top_k]