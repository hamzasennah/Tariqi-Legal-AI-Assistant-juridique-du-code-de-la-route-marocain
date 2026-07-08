from __future__ import annotations

from tariqi.chunking import chunk_documents
from tariqi.config import AppConfig
from tariqi.loaders import load_seed_corpus


if __name__ == "__main__":
    config = AppConfig.from_env()
    chunks = chunk_documents(load_seed_corpus(config.corpus_path))
    print(f"Chunks créés : {len(chunks)}")
