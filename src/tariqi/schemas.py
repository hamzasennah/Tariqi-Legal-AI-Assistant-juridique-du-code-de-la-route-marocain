from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class LegalDocument:
    id: str
    source_id: str
    authority: str
    title: str
    document: str
    article_or_section: str
    date_source: str
    language: str
    theme: str
    trust_level: str
    url: str
    text: str

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "LegalDocument":
        return cls(
            id=str(data["id"]),
            source_id=str(data.get("source_id", data["id"])),
            authority=str(data.get("authority", "")),
            title=str(data.get("title", "")),
            document=str(data.get("document", "")),
            article_or_section=str(data.get("article_or_section", "")),
            date_source=str(data.get("date_source", "")),
            language=str(data.get("language", "fr")),
            theme=str(data.get("theme", "general")),
            trust_level=str(data.get("trust_level", "C")),
            url=str(data.get("url", "")),
            text=str(data.get("text", "")),
        )

    def metadata(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("text", None)
        return data


@dataclass(frozen=True)
class DocumentChunk:
    id: str
    source_id: str
    text: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentChunk":
        return cls(
            id=str(data["id"]),
            source_id=str(data["source_id"]),
            text=str(data["text"]),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass(frozen=True)
class ScoredChunk:
    chunk: DocumentChunk
    score: float

    def source_line(self) -> str:
        meta = self.chunk.metadata
        authority = meta.get("authority", "Source inconnue")
        title = meta.get("title", self.chunk.source_id)
        section = meta.get("article_or_section", "")
        return f"{authority} - {title} - {section} | score={self.score:.3f}"


@dataclass(frozen=True)
class RAGAnswer:
    question: str
    answer_text: str
    sources: list[ScoredChunk]
    confidence: str
    used_llm: bool

    def to_markdown(self) -> str:
        if "### Sources" in self.answer_text:
            return self.answer_text

        source_lines = "\n".join(f"- {item.source_line()}" for item in self.sources)
        return (
            f"{self.answer_text}\n\n"
            f"### Sources utilisées\n"
            f"{source_lines or '- Aucune source pertinente trouvée.'}\n\n"
            f"### Niveau de confiance\n"
            f"{self.confidence}"
        )
