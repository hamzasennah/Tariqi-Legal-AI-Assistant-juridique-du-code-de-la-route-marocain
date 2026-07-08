from __future__ import annotations

from .config import AppConfig
from .cleaning import normalize_for_search
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
        initial = store.search(query_embedding, top_k=max(top_k * 4, top_k))
        reranked = self._rerank(question, initial)
        return reranked[:top_k]

    def _rerank(self, question: str, chunks: list[ScoredChunk]) -> list[ScoredChunk]:
        normalized_question = normalize_for_search(question)
        question_tokens = normalized_question.split()
        token_set = set(question_tokens)
        bigrams = {
            f"{a} {b}"
            for a, b in zip(question_tokens, question_tokens[1:])
            if len(a) > 2 and len(b) > 2
        }

        adjusted: list[ScoredChunk] = []
        for item in chunks:
            searchable = normalize_for_search(
                " ".join(
                    [
                        item.chunk.text,
                        str(item.chunk.metadata.get("title", "")),
                        str(item.chunk.metadata.get("article_or_section", "")),
                        str(item.chunk.metadata.get("theme", "")),
                    ]
                )
            )
            chunk_tokens = set(searchable.split())
            lexical_overlap = len(token_set & chunk_tokens) / max(len(token_set), 1)
            phrase_bonus = 0.0
            for bigram in bigrams:
                if bigram in searchable:
                    phrase_bonus += 0.10
            adjusted_score = item.score + (0.06 * lexical_overlap) + min(phrase_bonus, 0.20)
            adjusted.append(ScoredChunk(chunk=item.chunk, score=adjusted_score))

        adjusted.sort(key=lambda item: item.score, reverse=True)
        return adjusted
