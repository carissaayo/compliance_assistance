def chunk_pages(
    pages: list[dict[str, int | str]],
    chunk_size: int = 1600,
    overlap: int = 240,
) -> list[dict]:
    chunks = []
    step = chunk_size - overlap
    position= 0
    
    for page in pages:
        content= page["text"]
        page_number = page['page_number']
        start=0
        while start < len(content):
            position += 1
            window = content[start : start + chunk_size]

            chunks.append(
                {
                    "content": window,
                    "page_reference": page_number,
                    "position": position,
                }
            )

            start += step

           
