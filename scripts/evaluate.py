from __future__ import annotations

import csv
from pathlib import Path

from _path import ROOT  # noqa: F401
from tariqi import AppConfig, TariqiAssistant


def main() -> None:
    config = AppConfig.from_env()
    assistant = TariqiAssistant(config)
    input_path = ROOT / "data" / "structured" / "evaluation_questions.csv"
    output_path = ROOT / "outputs" / "evaluation_results.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open(encoding="utf-8", newline="") as file:
        questions = list(csv.DictReader(file))

    rows: list[dict[str, str]] = []
    for item in questions:
        answer = assistant.ask(item["question"], top_k=5)
        top_source = answer.sources[0].chunk.source_id if answer.sources else ""
        rows.append(
            {
                "id": item["id"],
                "question": item["question"],
                "expected_source_id": item["expected_source_id"],
                "top_source_id": top_source,
                "confidence": answer.confidence,
                "match": str(top_source == item["expected_source_id"]),
            }
        )

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Évaluation écrite dans {output_path}")


if __name__ == "__main__":
    main()
