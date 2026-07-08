from __future__ import annotations

import hashlib
import math
import re
from abc import ABC, abstractmethod

from .config import AppConfig
from .cleaning import normalize_for_search


_TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


class EmbeddingBackend(ABC):
    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


class HashingEmbeddingBackend(EmbeddingBackend):
    """Small deterministic embedding backend for demos and tests.

    It is not as semantic as transformer/OpenAI embeddings, but it keeps the
    full RAG pipeline runnable without credentials.
    """

    def __init__(self, dimensions: int = 384) -> None:
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = _TOKEN_RE.findall(normalize_for_search(text))
        features = tokens + [f"{a}_{b}" for a, b in zip(tokens, tokens[1:])]

        for feature in features:
            digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
            value = int.from_bytes(digest, "big")
            index = value % self.dimensions
            sign = -1.0 if (value >> 9) & 1 else 1.0
            vector[index] += sign

        norm = math.sqrt(sum(item * item for item in vector))
        if norm == 0:
            return vector
        return [item / norm for item in vector]


class OpenAIEmbeddingBackend(EmbeddingBackend):
    def __init__(self, api_key: str, model: str) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install openai to use OpenAI embeddings.") from exc

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]


def create_embedding_backend(config: AppConfig) -> EmbeddingBackend:
    if config.embedding_backend == "openai":
        if not config.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when TARIQI_EMBEDDING_BACKEND=openai.")
        return OpenAIEmbeddingBackend(config.openai_api_key, config.openai_embedding_model)
    return HashingEmbeddingBackend()
