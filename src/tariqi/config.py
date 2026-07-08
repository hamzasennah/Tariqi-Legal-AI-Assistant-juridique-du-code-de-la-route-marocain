from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def resolve_project_path(value: str | Path) -> Path:
    """Resolve a path relative to the project root."""
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def as_bool(value: str | bool | None, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def answer_mode_enabled(value: str | None, api_key: str | None) -> bool:
    """Resolve the answer-generation mode.

    "auto" means: use the LLM only when an API key exists. This avoids showing
    a broken LLM mode to users who run the project locally without credentials.
    """
    if value is None or value.strip().lower() == "auto":
        return bool(api_key)
    return as_bool(value, default=False)


@dataclass(frozen=True)
class AppConfig:
    corpus_path: Path
    infractions_csv: Path
    procedures_path: Path
    source_manifest_path: Path
    index_path: Path
    embedding_backend: str
    openai_api_key: str | None
    openai_generation_model: str
    openai_embedding_model: str
    use_openai_answer: bool

    @classmethod
    def from_env(cls) -> "AppConfig":
        load_dotenv(PROJECT_ROOT / ".env")

        api_key = os.getenv("OPENAI_API_KEY") or None
        answer_mode = os.getenv("TARIQI_USE_OPENAI_ANSWER", "auto")

        return cls(
            corpus_path=resolve_project_path(
                os.getenv("TARIQI_CORPUS_PATH", "data/seed/legal_corpus.jsonl")
            ),
            infractions_csv=resolve_project_path(
                os.getenv("TARIQI_INFRACTIONS_CSV", "data/structured/infractions_maroc.csv")
            ),
            procedures_path=resolve_project_path(
                os.getenv("TARIQI_PROCEDURES_PATH", "data/structured/procedures.json")
            ),
            source_manifest_path=resolve_project_path(
                os.getenv("TARIQI_SOURCE_MANIFEST", "data/raw/sources_manifest.json")
            ),
            index_path=resolve_project_path(
                os.getenv("TARIQI_INDEX_PATH", "vectorstore/tariqi_index.json")
            ),
            embedding_backend=os.getenv("TARIQI_EMBEDDING_BACKEND", "hashing").strip().lower(),
            openai_api_key=api_key,
            openai_generation_model=os.getenv("OPENAI_GENERATION_MODEL", "gpt-5.5"),
            openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            use_openai_answer=answer_mode_enabled(answer_mode, api_key),
        )
