from __future__ import annotations

import json
from pathlib import Path

from .cleaning import clean_text
from .schemas import LegalDocument


def load_seed_corpus(path: Path) -> list[LegalDocument]:
    documents: list[LegalDocument] = []
    if not path.exists():
        return documents

    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            documents.append(LegalDocument.from_mapping(json.loads(line)))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_no}") from exc

    return documents


def extract_text_from_html(path: Path) -> str:
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise RuntimeError("Install beautifulsoup4 to extract HTML files.") from exc

    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()
    return clean_text(soup.get_text(" "))


def extract_text_from_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("Install pypdf to extract PDF files.") from exc

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return clean_text("\n".join(pages))


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".html", ".htm"}:
        return extract_text_from_html(path)
    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    return clean_text(path.read_text(encoding="utf-8", errors="ignore"))


def load_raw_documents(raw_dir: Path) -> list[LegalDocument]:
    documents: list[LegalDocument] = []
    if not raw_dir.exists():
        return documents

    ignored = {"README.md", "sources_manifest.json"}
    allowed = {".txt", ".md", ".html", ".htm", ".pdf"}

    for path in sorted(raw_dir.rglob("*")):
        if not path.is_file() or path.name in ignored or path.suffix.lower() not in allowed:
            continue
        text = extract_text(path)
        if not text:
            continue
        source_id = path.stem.lower().replace(" ", "_")
        documents.append(
            LegalDocument(
                id=f"raw_{source_id}",
                source_id=source_id,
                authority="Source brute locale",
                title=path.stem,
                document=path.name,
                article_or_section="Document importé",
                date_source="non renseignée",
                language="fr",
                theme="raw",
                trust_level="B",
                url=str(path),
                text=text,
            )
        )

    return documents
