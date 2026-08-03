def chunk_pages(
    pages: list[dict[str, int | str]],
    chunk_size: int = 1600,
    overlap: int = 240,
) -> list[dict[str, int | str]]:
    if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

    chunks: list[dict[str, int | str]] = []
    step = chunk_size - overlap

    for page in pages:
        content = str(page["text"]).strip()
        if not content:
            continue

        start = 0
        while start < len(content):
            window = content[start : start + chunk_size]

            chunks.append(
                {
                    "content": window,
                    "token_count": max(1, len(window) // 4),
                    "page_reference": str(page["page_number"]),
                    "position": len(chunks),
                }
            )
            if start + chunk_size >= len(content):
                break
            start += step

    return chunks
