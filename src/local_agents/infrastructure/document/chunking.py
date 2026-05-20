def chunk_text(text: str, *, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks by character count."""
    normalized = " ".join(text.split())
    if not normalized:
        return []
    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = start + chunk_size
        chunks.append(normalized[start:end])
        if end >= len(normalized):
            break
        start = max(0, end - overlap)
    return chunks
