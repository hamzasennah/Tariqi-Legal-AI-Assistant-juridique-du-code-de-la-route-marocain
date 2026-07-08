from __future__ import annotations

from .cleaning import clean_text
from .schemas import DocumentChunk, LegalDocument


def chunk_words(words: list[str], chunk_size: int, overlap: int) -> list[list[str]]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be lower than chunk_size")

    chunks: list[list[str]] = []
    start = 0
    step = chunk_size - overlap

    while start < len(words):
        chunk = words[start : start + chunk_size]
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks


def chunk_document(
    document: LegalDocument,
    chunk_size_words: int = 180,
    overlap_words: int = 35,
) -> list[DocumentChunk]:
    text = clean_text(document.text)
    words = text.split()
    raw_chunks = chunk_words(words, chunk_size_words, overlap_words)
    chunks: list[DocumentChunk] = []

    for index, chunk in enumerate(raw_chunks):
        chunk_text = " ".join(chunk)
        chunks.append(
            DocumentChunk(
                id=f"{document.id}__chunk_{index:03d}",
                source_id=document.source_id,
                text=chunk_text,
                metadata={
                    **document.metadata(),
                    "chunk_index": index,
                    "chunk_size_words": len(chunk),
                },
            )
        )

    return chunks


def chunk_documents(
    documents: list[LegalDocument],
    chunk_size_words: int = 180,
    overlap_words: int = 35,
) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for document in documents:
        chunks.extend(chunk_document(document, chunk_size_words, overlap_words))
    return chunks
