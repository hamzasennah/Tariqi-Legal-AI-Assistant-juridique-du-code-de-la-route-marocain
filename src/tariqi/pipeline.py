from __future__ import annotations

from dataclasses import dataclass

from .chunking import chunk_documents
from .config import AppConfig, PROJECT_ROOT
from .embeddings import create_embedding_backend
from .loaders import load_raw_documents, load_seed_corpus
from .schemas import DocumentChunk
from .vector_store import JsonVectorStore


@dataclass(frozen=True)
class BuildReport:
    documents_count: int
    chunks_count: int
    index_path: str
    embedding_backend: str


def build_index(
    config: AppConfig | None = None,
    include_raw: bool = False,
    chunk_size_words: int = 180,
    overlap_words: int = 35,
) -> BuildReport:
    config = config or AppConfig.from_env()
    documents = load_seed_corpus(config.corpus_path)

    if include_raw:
        documents.extend(load_raw_documents(PROJECT_ROOT / "data" / "raw"))

    chunks: list[DocumentChunk] = chunk_documents(
        documents,
        chunk_size_words=chunk_size_words,
        overlap_words=overlap_words,
    )

    if not chunks:
        raise RuntimeError("No document chunks available. Check the corpus and raw data paths.")

    backend = create_embedding_backend(config)
    embeddings = backend.embed_documents([chunk.text for chunk in chunks])

    store = JsonVectorStore()
    for chunk, embedding in zip(chunks, embeddings):
        store.add(chunk, embedding)
    store.save(config.index_path)

    return BuildReport(
        documents_count=len(documents),
        chunks_count=len(chunks),
        index_path=str(config.index_path),
        embedding_backend=config.embedding_backend,
    )
