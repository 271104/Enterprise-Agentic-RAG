"""Paragraph-aware text chunking with a strict character limit."""

import logfire


def _split_oversized_paragraph(paragraph: str, chunk_size: int) -> list[str]:
    """Split long paragraphs at whitespace while keeping every piece bounded."""
    pieces: list[str] = []
    remaining = paragraph
    while len(remaining) > chunk_size:
        boundary = remaining.rfind(" ", 0, chunk_size + 1)
        if boundary <= 0:
            boundary = chunk_size
        pieces.append(remaining[:boundary].strip())
        remaining = remaining[boundary:].strip()
    if remaining:
        pieces.append(remaining)
    return pieces


def chunk_text(text: str, chunk_size: int = 1500) -> list[str]:
    """Split text into non-empty chunks no longer than ``chunk_size`` chars."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    if not text or not text.strip():
        return []

    with logfire.span("Text chunking", text_length=len(text), chunk_size=chunk_size):
        paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
        chunks: list[str] = []
        current = ""

        for paragraph in paragraphs:
            parts = _split_oversized_paragraph(paragraph, chunk_size)
            for part in parts:
                candidate = f"{current}\n\n{part}" if current else part
                if len(candidate) <= chunk_size:
                    current = candidate
                else:
                    if current:
                        chunks.append(current)
                    current = part

        if current:
            chunks.append(current)
        logfire.info("Text chunks generated", count=len(chunks))
        return chunks
