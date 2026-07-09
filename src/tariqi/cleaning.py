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
    "consequence",
    "consequences",
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
    "mon",
    "par",
    "peut",
    "permet",
    "permettre",
    "police",
    "pourquoi",
    "probleme",
    "problemes",
    "pour",
    "que",
    "quel",
    "quelle",
    "quelles",
    "qui",
    "quoi",
    "risque",
    "sans",
    "sont",
    "sur",
    "un",
    "une",
    "trouver",
    "vehicule",
    "vehicules",
    "voiture",
    "voitures",
    "vous",
    "conducteur",
    "conducteurs",
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
    "paye": {"paiement", "payer"},
    "payee": {"paiement", "payer"},
    "payees": {"paiement", "payer"},
    "payes": {"paiement", "payer"},
    "pay": {"paiement", "payer"},
    "retir": {"retrait"},
    "retire": {"retrait"},
    "retiree": {"retrait"},
    "retirees": {"retrait"},
    "retires": {"retrait"},
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
        expanded.update(token_variants(token))
    return expanded


def matched_query_tokens(query_tokens: set[str], target_tokens: set[str]) -> set[str]:
    matched = set()
    target_variants = expanded_query_tokens(target_tokens)
    for token in query_tokens:
        query_variants = token_variants(token) | QUERY_SYNONYMS.get(token, set()) | {token}
        if query_variants & target_variants:
            matched.add(token)
    return matched


def token_variants(token: str) -> set[str]:
    variants = {token}
    if token.startswith("pay"):
        variants.add("pai" + token[3:])

    suffixes = (
        "ations",
        "ation",
        "itions",
        "ition",
        "ements",
        "ement",
        "issant",
        "issants",
        "antes",
        "ante",
        "ants",
        "ant",
        "ees",
        "es",
        "ee",
        "er",
        "ez",
        "s",
        "e",
    )
    for suffix in suffixes:
        if len(token) > len(suffix) + 3 and token.endswith(suffix):
            variants.add(token[: -len(suffix)])

    if len(token) >= 5:
        variants.add(token[:5])
    if len(token) >= 7:
        variants.add(token[:6])

    return {variant for variant in variants if len(variant) >= 3}
