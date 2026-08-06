from sqlalchemy.orm import Session

from app.models.document import Document


def get_document_by_id(document_id: int, db: Session) -> Document | None:
    document = db.get(Document, document_id)
    return document