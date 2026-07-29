import hashlib
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.document import Document

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

DbSession = Annotated[Session, Depends(get_db)] 

@router.post("/")
async def upload_document(file: UploadFile, db: DbSession):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    contents = await file.read()
    content_hash = hashlib.sha256(contents).hexdigest()

    existing = db.scalar(select(Document).where(Document.content_hash == content_hash))
    if existing:
        return {    
            "id":existing.id,
            "filename": existing.filename,
            "content_hash": existing.content_hash,
            "status":existing.status,
            "message":"Document already exists - skipped re-uploading",
        }
    

    save_path = UPLOAD_DIR / f"{content_hash}.pdf"
    save_path.write_bytes(contents)
    
    doc = Document(
        filename=file.filename,
        content_hash=content_hash,
        status="pending",
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "id": doc.id,
        "filename": doc.filename,
        "content_hash": doc.content_hash,
        "status": doc.status,
        "message": "Document uploaded successfully",
    }