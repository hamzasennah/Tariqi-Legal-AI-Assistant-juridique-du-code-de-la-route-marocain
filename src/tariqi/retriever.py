from __future__ import annotations

from .config import AppConfig
from .cleaning import meaningful_tokens, normalize_for_search
from .embeddings import create_embedding_backend
from .pipeline import build_index
from .schemas import ScoredChunk
from .vector_store import JsonVectorStore


MIN_RELEVANCE_SCORE = 0.20
MIN_QUERY_TOKEN_COUNT = 1


class Retriever:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or AppConfig.from_env()
        self.embedding_backend = create_embedding_backend(self.config)

    def retrieve(self, question: str, top_k: int = 5) -> list[ScoredChunk]:
        query_tokens = meaningful_tokens(question)
        if len(query_tokens) < MIN_QUERY_TOKEN_COUNT:
            return []

        if self._index_needs_rebuild():
            build_index(self.config)

        store = JsonVectorStore.load(self.config.index_path)
        query_embedding = self.embedding_backend.embed_query(question)
        initial = store.search(query_embedding, top_k=max(top_k * 4, top_k))
        reranked = self._rerank(question, initial)
        relevant = [
            item
            for item in reranked
            if item.score >= MIN_RELEVANCE_SCORE
            and self._has_lexical_anchor(question, item)
        ]
        return relevant[:top_k]

    def _index_needs_rebuild(self) -> bool:
        if not self.config.index_path.exists():
            return True

        try:
            return self.config.corpus_path.stat().st_mtime > self.config.index_path.stat().st_mtime
        except OSError:
            return False

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

    def _has_lexical_anchor(self, question: str, item: ScoredChunk) -> bool:
        query_tokens = meaningful_tokens(question)
        if not query_tokens:
            return False

        searchable_tokens = meaningful_tokens(
            " ".join(
                [
                    item.chunk.text,
                    str(item.chunk.metadata.get("title", "")),
                    str(item.chunk.metadata.get("article_or_section", "")),
                    str(item.chunk.metadata.get("theme", "")),
                ]
            )
        )
        return bool(query_tokens & searchable_tokens)
