import hashlib
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/")
async def upload_document(file: UploadFile):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    contents = await file.read()
    content_hash = hashlib.sha256(contents).hexdigest()

    save_path = UPLOAD_DIR/ f"{content_hash}.pdf"
    save_path.write_bytes(contents)

    return {
        "filename": file.filename,
        "content_hash": content_hash,
        "saved_path": str(save_path),
    }