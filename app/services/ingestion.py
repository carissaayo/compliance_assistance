from pathlib import Path

from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document, DocumentStatus
from app.services.chunker import chunk_pages
from app.services.embedding.factory import get_embedding_provider
from app.services.pdf_extractor import extract_text_by_page


def ingest_document(db: Session, document: Document, file_path:Path) ->Document:
    document.status = DocumentStatus.processing
    db.commit()

    try:
        pages = extract_text_by_page(file_path)
        chunk_data = chunk_pages(pages)
        
        if not chunk_data:
            document.status = DocumentStatus.failed
            db.commit()
            db.refresh(document)
            return document

        provider = get_embedding_provider()
        vectors = provider.embed([item["content"] for item in chunk_data])

        for item, vector in zip(chunk_data, vectors, strict=True):
            db.add(
                Chunk(
                document_id = document.id,
                position = item['position'],
                content = item['content'],
                token_count =item["token_count"],
                page_reference = item['page_reference'],
                embedding= vector,
            ))

        document.status = DocumentStatus.completed
        db.commit()
        db.refresh(document)
        return document
    except Exception:
        db.rollback()
        document = db.get(Document, document.id)
        if document is not None:
            document.status = DocumentStatus.failed
            db.commit()
            
        raise