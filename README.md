# NaijaPay Compliance Assistant

A retrieval-augmented question-answering system over Nigerian statutory payroll and tax
documentation — PAYE (Personal Income Tax Act), the Finance Act, PenCom pension
regulations, NSITF, NHF, and ITF guidelines.

**Why this exists:** Nigerian HR/finance teams constantly need to answer questions like
*"does a non-taxable transport allowance count toward the pension contribution base?"*
or *"what's the current consolidated relief allowance formula after the latest Finance
Act amendment?"* — answers that live scattered across PDFs, circulars, and amendments
that override earlier clauses. This project builds a system that answers those
questions **grounded in the actual source documents**, with citations, rather than an
LLM guessing from training data (which is exactly the failure mode you cannot afford in
a compliance context).

This is a portfolio/learning project built to demonstrate production RAG engineering —
ingestion, retrieval, generation, evaluation, and the operational concerns (cost,
latency, failure handling) that separate a working system from a notebook demo.

---



## Document set


| Source                                            | Content                                                 | Why it's a good test case                                                                                    |
| ------------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| FIRS PAYE guidelines + tax tables                 | PAYE bands, reliefs, computation rules                  | Tables embedded in prose; numeric precision matters                                                          |
| Finance Act (relevant sections, latest amendment) | Statutory changes to PIT, CIT provisions                | Amendments override earlier text — tests whether retrieval surfaces the *current* rule, not a superseded one |
| PenCom Pension Reform Act summary                 | Contribution rates, voluntary contributions, exemptions | Cross-references PAYE definitions of taxable income                                                          |
| NSITF / ITF guidelines                            | Employer contribution obligations                       | Shorter, more structured — a "should be easy" retrieval baseline                                             |
| NHF circulars                                     | Contribution rate, eligibility                          | Sparse documents — tests behavior when there's little supporting context                                     |


All public documents, downloaded as PDFs and left in their native (occasionally messy)
formatting rather than pre-cleaned, since that's the realistic ingestion problem.

---



## Architecture

```
Upload (PDF) → Ingestion worker → Chunk → Embed → pgvector
                                                       │
User question → Hybrid retrieve (vector + BM25) → Rerank → Context assembly → LLM → Answer + citations
```



### Ingestion

- FastAPI endpoint accepts a PDF, stores the raw file, enqueues a background job
(Celery + Redis) — embedding is never called synchronously in the request path.
- Documents are hashed on content; re-uploading a previously-ingested document is a
no-op rather than a re-embed, mirroring idempotency handling from prior production
payment/webhook work.
- Chunking: fixed-size token windows (~400 tokens, 15% overlap) as the baseline,
deliberately naive at first — see **Decisions** below for why, and what changing this
did to eval scores.



### Retrieval

- pgvector for embedding storage — chosen to avoid introducing a new database
operationally, since Postgres is already the system of record.
- Hybrid: vector similarity (top 20) + Postgres full-text/BM25 (top 20), merged and
deduplicated, then reranked with a cross-encoder down to top 5.
- Pure vector search on its own under-retrieves exact statutory terms (section numbers,
specific rate figures) that a keyword match catches reliably — hence hybrid rather
than vector-only.



### Generation

- Context assembled from the top 5 reranked chunks, with an explicit token budget;
truncation is logged, never silent.
- Answers are required to cite the source document and section for every claim; if
retrieval confidence is low, the system says so rather than answering from the base
model's general knowledge — enforced via prompt instruction plus a retrieval-score
threshold that triggers an "insufficient grounding" response.
- Streaming responses via FastAPI.



### Evaluation

- Golden set of ~30 questions built from actual payroll scenarios (drawing on prior
PeopleHQ payroll-engine work), each with an expected source section and expected
answer content.
- Retrieval and generation scored separately:
  - **Retrieval accuracy**: did the correct source chunk appear in the top-k?
  - **Answer correctness**: does the generated answer match expected content, scored
  with an LLM-as-judge plus manual spot-check?
- Eval suite reruns automatically when chunking strategy, embedding model, or reranking
changes, with results logged so regressions are visible — not just "it feels better."



### Production concerns

- Retries with backoff on LLM/embedding API calls (rate limits and timeouts are routine,
not exceptional).
- Per-request logging of input/output token counts, estimated cost, and latency.
- Basic per-user rate limiting.
- `/health` endpoint and an `/evals/latest` endpoint exposing current eval scores, so the
system is demoable rather than a one-off script.

---



## Decisions log

This section is the point of the project — a running record of what was chosen, why,
and what changed when it was tested.


| Decision           | Choice                                                                   | Rationale                                                                                                                             | Eval impact                            |
| ------------------ | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| Chunking           | Fixed 400-token windows, 15% overlap (baseline)                          | Cheapest to implement correctly first; establishes a measurable floor before adding complexity                                        | *fill in after first eval run*         |
| Retrieval          | Hybrid vector + BM25 over vector-only                                    | Statutory documents contain exact terms (rates, section numbers) that embeddings alone under-retrieve                                 | *fill in after A/B*                    |
| Vector store       | pgvector over a dedicated vector DB                                      | No new operational dependency; team already runs Postgres                                                                             | N/A (operational, not accuracy-driven) |
| Ungrounded answers | Refuse rather than answer from model priors below a confidence threshold | Wrong compliance answers are worse than no answer                                                                                     | *fill in false-positive/negative rate* |
| Background jobs    | Celery + Redis over synchronous embedding calls                          | Embedding APIs are slow and rate-limited; blocking the request thread doesn't scale, matches prior BullMQ-based async pipeline design | N/A (operational)                      |


*(To be filled in as the project is built — this table is the primary artifact for
interviews: it shows judgment, not just output.)*

---



## Setup

```bash
# clone and enter
git clone <repo-url> && cd naijapay-rag

# environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set OPENAI_API_KEY (or equivalent), DATABASE_URL, REDIS_URL

# database
docker compose up -d postgres redis
alembic upgrade head    # creates tables + pgvector extension

# run
uvicorn app.main:app --reload
celery -A app.worker worker --loglevel=info   # in a separate terminal

# ingest sample documents
python scripts/ingest.py --dir ./data/sample_docs

# run evals
python scripts/run_evals.py
```



## Assumptions

- LLM provider: OpenAI (swappable via a thin provider interface — same pattern as the
Flutterwave provider abstraction in prior fintech work, to avoid vendor lock-in in
code structure).
- Embedding model and reranker choices are logged in `config.py` and versioned, since
changing either invalidates existing embeddings and requires a re-index.
- This is a Q&A assistant, not a source of legal/tax advice — every answer includes a
disclaimer and a citation back to the source document for independent verification.



## Roadmap / not yet built

- [ ] Multi-turn conversation with retrieval-aware follow-ups
- [ ] Automatic re-ingestion when a tracked source document is updated upstream
- [ ] Confidence calibration study (does the stated confidence match actual accuracy?)