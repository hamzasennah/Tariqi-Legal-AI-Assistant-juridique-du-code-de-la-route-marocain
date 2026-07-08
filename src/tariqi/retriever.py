from __future__ import annotations

from .config import AppConfig
from .embeddings import create_embedding_backend
from .pipeline import build_index
from .schemas import ScoredChunk
from .vector_store import JsonVectorStore


class Retriever:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or AppConfig.from_env()
        self.embedding_backend = create_embedding_backend(self.config)

    def retrieve(self, question: str, top_k: int = 5) -> list[ScoredChunk]:
        if not self.config.index_path.exists():
            build_index(self.config)

        store = JsonVectorStore.load(self.config.index_path)
        query_embedding = self.embedding_backend.embed_query(question)
        return store.search(query_embedding, top_k=top_k)
