from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SourceRegistry:
    def __init__(self, sources: list[dict[str, Any]]) -> None:
        self.sources = sources
        self._by_id = {str(item["id"]): item for item in sources}

    @classmethod
    def from_json(cls, path: Path) -> "SourceRegistry":
        if not path.exists():
            return cls([])
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def get(self, source_id: str) -> dict[str, Any] | None:
        return self._by_id.get(source_id)

    def trusted_sources(self) -> list[dict[str, Any]]:
        return [
            item
            for item in self.sources
            if str(item.get("trust_level", "")).upper() in {"A+", "A"}
        ]
