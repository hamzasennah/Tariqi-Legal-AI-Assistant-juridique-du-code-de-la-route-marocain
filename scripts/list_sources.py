from __future__ import annotations

from _path import ROOT  # noqa: F401
from tariqi.config import AppConfig
from tariqi.source_registry import SourceRegistry


def main() -> None:
    config = AppConfig.from_env()
    registry = SourceRegistry.from_json(config.source_manifest_path)

    for source in registry.sources:
        print(
            f"[{source.get('trust_level')}] {source.get('authority')} - "
            f"{source.get('title')} ({source.get('theme')})"
        )
        print(f"    {source.get('url')}")


if __name__ == "__main__":
    main()
