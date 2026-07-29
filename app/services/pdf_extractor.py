from pathlib import Path

import pdfplumber


def extract_text_by_page(file_path:Path) -> list[dict]:
    """
    Returns a list of {"page_number": int, "text": str} dicts,
    one per page in the PDF.
    """
    pages: list[dict[str, int | str]] = []
    
    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                }
            )
    return pages