from __future__ import annotations

from tariqi.config import AppConfig
from tariqi.loaders import load_seed_corpus


if __name__ == "__main__":
    config = AppConfig.from_env()
    documents = load_seed_corpus(config.corpus_path)
    print(f"Documents seed extraits : {len(documents)}")
