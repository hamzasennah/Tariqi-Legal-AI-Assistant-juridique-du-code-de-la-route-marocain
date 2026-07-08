from __future__ import annotations

import pytest

from tariqi.chunking import chunk_document, chunk_words
from tariqi.schemas import LegalDocument


def test_chunk_words_uses_overlap() -> None:
    words = "a b c d e f g".split()
    chunks = chunk_words(words, chunk_size=3, overlap=1)
    assert chunks == [
        ["a", "b", "c"],
        ["c", "d", "e"],
        ["e", "f", "g"],
        ["g"],
    ]


def test_chunk_words_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError):
        chunk_words(["a"], chunk_size=3, overlap=3)


def test_chunk_document_preserves_metadata() -> None:
    document = LegalDocument(
        id="doc_test",
        source_id="source_test",
        authority="NARSA",
        title="Titre",
        document="Document",
        article_or_section="Section",
        date_source="2026-07-08",
        language="fr",
        theme="test",
        trust_level="A",
        url="https://example.test",
        text="un deux trois quatre cinq six",
    )

    chunks = chunk_document(document, chunk_size_words=4, overlap_words=1)

    assert len(chunks) == 2
    assert chunks[0].source_id == "source_test"
    assert chunks[0].metadata["authority"] == "NARSA"
    assert chunks[0].metadata["chunk_index"] == 0
