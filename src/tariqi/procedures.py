from __future__ import annotations

import json
from pathlib import Path

from .cleaning import matched_query_tokens, meaningful_tokens, normalize_for_search
from .config import AppConfig


class ProcedureGuide:
    def __init__(self, path: Path | None = None) -> None:
        config = AppConfig.from_env()
        self.path = path or config.procedures_path
        self.procedures = json.loads(self.path.read_text(encoding="utf-8"))

    def match(self, query: str) -> dict | None:
        normalized_query = normalize_for_search(query)
        best_rank = (0, 0)
        best = None
        query_tokens = meaningful_tokens(query)

        for procedure in self.procedures:
            score = 0
            specific_score = 0
            for keyword in procedure.get("trigger_keywords", []):
                normalized_keyword = normalize_for_search(keyword)
                keyword_tokens = meaningful_tokens(keyword)
                if normalized_keyword and normalized_keyword in normalized_query:
                    weight = self._keyword_weight(normalized_keyword)
                    score += weight
                    specific_score += weight if weight > 1 else 0
                else:
                    overlap = len(matched_query_tokens(query_tokens, keyword_tokens))
                    if overlap >= 2:
                        score += overlap
                        specific_score += overlap
            rank = (score, specific_score)
            if rank > best_rank:
                best_rank = rank
                best = procedure

        return best if best_rank[0] >= 2 else None

    def all(self) -> list[dict]:
        return list(self.procedures)

    def _keyword_weight(self, keyword: str) -> int:
        generic = {"amende", "contravention", "points"}
        if keyword in generic:
            return 1
        return 3 + len(keyword.split())
