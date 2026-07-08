from __future__ import annotations

import re
import unicodedata


_WHITESPACE_RE = re.compile(r"\s+")

STOPWORDS = {
    "a",
    "au",
    "aux",
    "avec",
    "ce",
    "cette",
    "combien",
    "comment",
    "dans",
    "de",
    "des",
    "du",
    "elle",
    "en",
    "est",
    "et",
    "faire",
    "il",
    "je",
    "la",
    "le",
    "les",
    "on",
    "ou",
    "par",
    "peut",
    "point",
    "points",
    "pour",
    "que",
    "quel",
    "quelle",
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


def clean_text(text: str) -> str:
    """Normalize legal text while keeping accents and punctuation."""
    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("\x00", " ")
    normalized = _WHITESPACE_RE.sub(" ", normalized)
    return normalized.strip()


def normalize_for_search(text: str) -> str:
    """Lowercase and strip accents for fuzzy matching."""
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return _WHITESPACE_RE.sub(" ", text).strip()


def meaningful_tokens(text: str) -> set[str]:
    """Return useful search tokens, excluding short words and common fillers."""
    normalized = normalize_for_search(text)
    return {
        token
        for token in normalized.split()
        if len(token) > 2 and token not in STOPWORDS
    }
