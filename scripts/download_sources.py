from __future__ import annotations

import argparse
import mimetypes
from pathlib import Path
from urllib.parse import urlparse

import requests

from _path import ROOT
from tariqi.config import AppConfig
from tariqi.source_registry import SourceRegistry


def extension_from_response(url: str, content_type: str | None) -> str:
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix
    if suffix:
        return suffix
    if content_type:
        guessed = mimetypes.guess_extension(content_type.split(";")[0].strip())
        if guessed:
            return guessed
    return ".html"


def main() -> None:
    parser = argparse.ArgumentParser(description="Download official sources listed in the manifest.")
    parser.add_argument("--only-trusted", action="store_true", help="Download only A+/A sources.")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds.")
    args = parser.parse_args()

    config = AppConfig.from_env()
    registry = SourceRegistry.from_json(config.source_manifest_path)
    sources = registry.trusted_sources() if args.only_trusted else registry.sources

    output_dir = ROOT / "data" / "raw" / "downloaded"
    output_dir.mkdir(parents=True, exist_ok=True)

    for source in sources:
        url = source.get("url")
        if not url:
            continue

        response = requests.get(url, timeout=args.timeout)
        response.raise_for_status()
        extension = extension_from_response(url, response.headers.get("content-type"))
        target = output_dir / f"{source['id']}{extension}"
        target.write_bytes(response.content)
        print(f"Téléchargé : {source['id']} -> {target}")


if __name__ == "__main__":
    main()
