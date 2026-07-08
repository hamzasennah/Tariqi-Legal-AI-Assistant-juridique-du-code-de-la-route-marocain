from __future__ import annotations

from pathlib import Path

from tariqi.config import AppConfig
from tariqi.pipeline import build_index
from tariqi.retriever import Retriever


ROOT = Path(__file__).resolve().parents[1]


def make_config(index_path: Path) -> AppConfig:
    return AppConfig(
        corpus_path=ROOT / "data" / "seed" / "legal_corpus.jsonl",
        infractions_csv=ROOT / "data" / "structured" / "infractions_maroc.csv",
        procedures_path=ROOT / "data" / "structured" / "procedures.json",
        source_manifest_path=ROOT / "data" / "raw" / "sources_manifest.json",
        index_path=index_path,
        embedding_backend="hashing",
        openai_api_key=None,
        openai_generation_model="gpt-5.5",
        openai_embedding_model="text-embedding-3-small",
        use_openai_answer=False,
    )


def test_build_index_and_retrieve_red_light(tmp_path: Path) -> None:
    config = make_config(tmp_path / "index.json")

    report = build_index(config)
    chunks = Retriever(config).retrieve("Combien de points pour un feu rouge ?", top_k=3)

    assert report.documents_count >= 10
    assert report.chunks_count >= report.documents_count
    assert chunks[0].chunk.source_id == "narsa_tableau_points_pdf"


def test_retrieve_sgg_consolidated_texts(tmp_path: Path) -> None:
    config = make_config(tmp_path / "index.json")

    build_index(config)
    chunks = Retriever(config).retrieve("Où trouver les textes consolidés du code de la route ?")

    assert chunks[0].chunk.source_id == "sgg_textes_consolides"
