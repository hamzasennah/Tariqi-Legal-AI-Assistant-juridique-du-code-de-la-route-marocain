from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .schemas import DocumentChunk, ScoredChunk


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class JsonVectorStore:
    def __init__(self, records: list[dict[str, Any]] | None = None) -> None:
        self.records = records or []

    def add(self, chunk: DocumentChunk, embedding: list[float]) -> None:
        self.records.append(
            {
                "chunk": chunk.to_dict(),
                "embedding": embedding,
            }
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "format": "tariqi-json-vectorstore-v1",
            "records": self.records,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "JsonVectorStore":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls(records=list(payload.get("records", [])))

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[ScoredChunk]:
        scored: list[ScoredChunk] = []
        for record in self.records:
            score = cosine_similarity(query_embedding, record["embedding"])
            scored.append(
                ScoredChunk(
                    chunk=DocumentChunk.from_dict(record["chunk"]),
                    score=score,
                )
            )
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]
