from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .cleaning import normalize_for_search
from .config import AppConfig


STOPWORDS = {
    "a",
    "au",
    "aux",
    "avec",
    "ce",
    "cette",
    "combien",
    "dans",
    "de",
    "des",
    "du",
    "elle",
    "en",
    "est",
    "et",
    "il",
    "je",
    "la",
    "le",
    "les",
    "on",
    "ou",
    "par",
    "point",
    "points",
    "pour",
    "que",
    "qui",
    "quoi",
    "retire",
    "retires",
    "risque",
    "sans",
    "sont",
    "sur",
    "un",
    "une",
    "vous",
}


@dataclass(frozen=True)
class FineResult:
    matched: bool
    query: str
    infraction: dict[str, str] | None
    delay: str
    amount: str | None
    points: str | None
    message: str


class FineCalculator:
    def __init__(self, csv_path: Path | None = None) -> None:
        config = AppConfig.from_env()
        self.csv_path = csv_path or config.infractions_csv
        self.rows = self._load_rows(self.csv_path)

    def _load_rows(self, path: Path) -> list[dict[str, str]]:
        with path.open(encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file))

    def search(self, query: str, limit: int = 5) -> list[dict[str, str]]:
        normalized_query = normalize_for_search(query)
        query_tokens = self._meaningful_tokens(normalized_query)
        if not query_tokens:
            return []

        scored: list[tuple[float, dict[str, str]]] = []

        for row in self.rows:
            label = normalize_for_search(row["nom_infraction"])
            label_tokens = self._meaningful_tokens(label)
            overlap = len(query_tokens & label_tokens)
            score = overlap / max(len(query_tokens), 1)
            if normalized_query and normalized_query in label:
                score += 1.0
            if score >= 0.35:
                scored.append((score, row))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [row for _, row in scored[:limit]]

    def calculate(self, query: str, delay: str = "24h") -> FineResult:
        matches = self.search(query, limit=1)
        if not matches:
            return FineResult(
                matched=False,
                query=query,
                infraction=None,
                delay=delay,
                amount=None,
                points=None,
                message="Aucune infraction correspondante dans le CSV structuré.",
            )

        row = matches[0]
        delay_key = self._delay_column(delay)
        amount = row.get(delay_key) or None
        points = row.get("points_retires") or None

        if not amount:
            message = (
                "Cette ligne ne contient pas de montant ATF simple. "
                "Il peut s'agir d'un délit ou d'un cas nécessitant une procédure judiciaire."
            )
        else:
            message = (
                f"Montant indicatif pour {delay}: {amount} DH. "
                f"Points à retirer: {points}. Source: {row.get('source')}."
            )

        return FineResult(
            matched=True,
            query=query,
            infraction=row,
            delay=delay,
            amount=amount,
            points=points,
            message=message,
        )

    def _delay_column(self, delay: str) -> str:
        normalized = normalize_for_search(delay)
        if "15" in normalized:
            return "montant_15j"
        if "30" in normalized:
            return "montant_30j"
        return "montant_24h"

    def _meaningful_tokens(self, normalized_text: str) -> set[str]:
        return {
            token
            for token in normalized_text.split()
            if len(token) > 1 and token not in STOPWORDS
        }
