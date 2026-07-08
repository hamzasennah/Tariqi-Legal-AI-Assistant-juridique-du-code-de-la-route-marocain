from __future__ import annotations

import argparse

from _path import ROOT  # noqa: F401
from tariqi import AppConfig, build_index


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Tariqi Legal AI vector index.")
    parser.add_argument("--include-raw", action="store_true", help="Include files from data/raw.")
    parser.add_argument("--chunk-size", type=int, default=180, help="Chunk size in words.")
    parser.add_argument("--overlap", type=int, default=35, help="Chunk overlap in words.")
    args = parser.parse_args()

    report = build_index(
        AppConfig.from_env(),
        include_raw=args.include_raw,
        chunk_size_words=args.chunk_size,
        overlap_words=args.overlap,
    )

    print("Index construit avec succès.")
    print(f"Documents : {report.documents_count}")
    print(f"Chunks : {report.chunks_count}")
    print(f"Backend embeddings : {report.embedding_backend}")
    print(f"Index : {report.index_path}")


if __name__ == "__main__":
    main()
