from pathlib import Path

import pdfplumber


def extract_text_by_page(file_path: Path) -> list[dict[str, int | str]]:
    """
    Returns a list of {"page_number": int, "text": str} dicts,
    one per page in the PDF.
    """
    pages: list[dict[str, int | str]] = []

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append({"page_number": page_number, "text": text})

    return pages


def extract_text_from_txt(file_path: Path) -> list[dict[str, int | str]]:
    """
    Reads a plain-text file and returns a single-page list so the rest of
    the ingestion pipeline (chunker, embedder) works without modification.
    """
    text = file_path.read_text(encoding="utf-8", errors="replace")
    return [{"page_number": 1, "text": text}]