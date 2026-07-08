from __future__ import annotations

import re
import unicodedata


_WHITESPACE_RE = re.compile(r"\s+")

STOPWORDS = {
    "a",
    "au",
    "aux",
    "avoir",
    "cas",
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
    "ici",
    "je",
    "la",
    "le",
    "les",
    "on",
    "ou",
    "par",
    "peut",
    "permet",
    "permettre",
    "police",
    "point",
    "points",
    "pourquoi",
    "probleme",
    "problemes",
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
    "vehicule",
    "vehicules",
    "voiture",
    "voitures",
    "vous",
}

QUERY_SYNONYMS = {
    "arreter": {"arret", "stationnement"},
    "arrete": {"arret", "stationnement"},
    "arreterai": {"arret", "stationnement"},
    "depasser": {"depassement"},
    "depasse": {"depassement"},
    "depasses": {"depassement", "depasser"},
    "depasserai": {"depassement"},
    "continu": {"continue"},
    "grille": {"franchissement", "non", "respect"},
    "griller": {"franchissement", "non", "respect"},
    "stopper": {"arret", "stationnement"},
    "stoppe": {"arret", "stationnement"},
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


def expanded_query_tokens(tokens: set[str]) -> set[str]:
    expanded = set(tokens)
    for token in tokens:
        expanded.update(QUERY_SYNONYMS.get(token, set()))
    return expanded


def matched_query_tokens(query_tokens: set[str], target_tokens: set[str]) -> set[str]:
    matched = set()
    for token in query_tokens:
        if token in target_tokens or QUERY_SYNONYMS.get(token, set()) & target_tokens:
            matched.add(token)
    return matched
