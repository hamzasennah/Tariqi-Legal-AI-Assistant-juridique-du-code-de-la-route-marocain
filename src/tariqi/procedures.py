from __future__ import annotations

import json
from pathlib import Path

from .cleaning import normalize_for_search
from .config import AppConfig


class ProcedureGuide:
    def __init__(self, path: Path | None = None) -> None:
        config = AppConfig.from_env()
        self.path = path or config.procedures_path
        self.procedures = json.loads(self.path.read_text(encoding="utf-8"))

    def match(self, query: str) -> dict | None:
        normalized_query = normalize_for_search(query)
        best_score = 0
        best = None

        for procedure in self.procedures:
            score = 0
            for keyword in procedure.get("trigger_keywords", []):
                normalized_keyword = normalize_for_search(keyword)
                if normalized_keyword and normalized_keyword in normalized_query:
                    score += 2
                else:
                    score += len(set(normalized_query.split()) & set(normalized_keyword.split()))
            if score > best_score:
                best_score = score
                best = procedure

        return best if best_score > 0 else None

    def all(self) -> list[dict]:
        return list(self.procedures)
