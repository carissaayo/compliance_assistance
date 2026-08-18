from app.config import settings
from app.db.session import DbSession
from app.models.answer_response import AnswerResponse
from app.models.chunk_response import ChunkResponse
from app.services.llm.factory import get_llm_provider
from app.services.retrieval import retrieve_vector

INSUFFICIENT_GROUNDING_MESSAGE = (
    "I don't have enough grounding in the uploaded documents to answer that."
)


def format_context(chunks: list[ChunkResponse]) -> str:
    parts: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        page = chunk.page_reference or "unknown"
        parts.append(f"[{index}] (page {page})\n{chunk.content}")
    return "\n\n".join(parts)


def build_prompt(question: str, context: str) -> str:
    return f"""You are a Q&A assistant over the provided source excerpts.

Rules:
- Answer only using the excerpts below.
- Cite sources like [1], [2] for every claim.
- If the excerpts do not contain the answer, say you cannot answer from the documents.
- Do not use general knowledge.
- Keep the answer concise and factual.

Question:
{question}

Excerpts:
{context}
"""


def generate_answer(db: DbSession, question: str) -> AnswerResponse:
    chunks = retrieve_vector(db, question)

    if not chunks or chunks[0].score > settings.retrieval_max_distance:
        return AnswerResponse(
            answer=INSUFFICIENT_GROUNDING_MESSAGE,
            grounded=False,
            sources=[],
        )

    context = format_context(chunks)
    prompt = build_prompt(question, context)
    answer = get_llm_provider().generate(prompt)

    return AnswerResponse(
        answer=answer,
        grounded=True,
        sources=chunks,
    )
