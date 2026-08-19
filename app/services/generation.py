import httpx

from app.config import settings
from app.db.session import DbSession
from app.models.answer_response import AnswerResponse
from app.models.chunk_response import ChunkResponse
from app.services.llm.factory import get_llm_provider
from app.services.retrieval import retrieve_hybrid

INSUFFICIENT_GROUNDING_MESSAGE = (
    "I don't have enough grounding in the uploaded documents to answer that."
)

LLM_TIMEOUT_MESSAGE = (
    "The language model took too long to respond. Try again or use a shorter question."
)

GENERATION_TOP_K = 3
MAX_CONTEXT_CHARS = 6000


def format_context(chunks: list[ChunkResponse]) -> str:
    parts: list[str] = []
    used = 0
    for i, chunk in enumerate(chunks, start=1):
        block = f"[{i}] (page {chunk.page_reference or 'unknown'})\n{chunk.content}"
        if used + len(block) > MAX_CONTEXT_CHARS:
            break
        parts.append(block)
        used += len(block)
    return "\n\n".join(parts)


def build_prompt(question: str, context: str) -> str:
    return f"""You are a Q&A assistant over the provided source excerpts.

Rules:
- Answer only using the excerpts below.
- Cite sources like [1], [2] for every claim.
- If the excerpts do not contain the answer, say you cannot answer from the documents.
- Do not use general knowledge.
- Keep the answer concise and factual.
- End with: "This is not legal or tax advice. Verify against the source documents."

Question:
{question}

Excerpts:
{context}
"""


def generate_answer(db: DbSession, question: str) -> AnswerResponse:
    chunks = retrieve_hybrid(db, question)
    prompt_chunks = chunks[:GENERATION_TOP_K]

    if not chunks:
        return AnswerResponse(
            answer=INSUFFICIENT_GROUNDING_MESSAGE,
            grounded=False,
            sources=[],
        )

    context = format_context(prompt_chunks)
    prompt = build_prompt(question, context)

    try:
        answer = get_llm_provider().generate(prompt)
    except httpx.ReadTimeout:
        return AnswerResponse(
            answer=LLM_TIMEOUT_MESSAGE,
            grounded=False,
            sources=[],
        )

    return AnswerResponse(
        answer=answer,
        grounded=True,
        sources=prompt_chunks,
    )
