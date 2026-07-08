from __future__ import annotations

from tariqi.config import AppConfig
from tariqi.embeddings import create_embedding_backend
from tariqi.loaders import load_seed_corpus


if __name__ == "__main__":
    config = AppConfig.from_env()
    backend = create_embedding_backend(config)
    documents = load_seed_corpus(config.corpus_path)
    embeddings = backend.embed_documents([document.text for document in documents])
    print(f"Embeddings créés : {len(embeddings)} avec backend {config.embedding_backend}")
