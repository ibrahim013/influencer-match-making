from __future__ import annotations

import re


def _word_pattern(name: str) -> re.Pattern[str]:
    escaped = re.escape(name.strip())
    return re.compile(rf"\b{escaped}\b", re.IGNORECASE)


def find_competitor_mentions(text: str, competitors: list[str]) -> list[str]:
    """Return competitor names detected in the draft (case-insensitive, word boundaries)."""
    hits: list[str] = []
    for name in competitors:
        if not name:
            continue
        if _word_pattern(name).search(text):
            hits.append(name)
    return hits


PLACEHOLDER_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\[[^\]]+\]"),  # [Insert Name Here]
    re.compile(r"\.{3,}"),  # ...
    re.compile(r"…+"),
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bXXX\b", re.IGNORECASE),
    re.compile(r"\bTBD\b", re.IGNORECASE),
]


def find_placeholders(text: str) -> list[str]:
    found: list[str] = []
    for pat in PLACEHOLDER_PATTERNS:
        for m in pat.finditer(text):
            found.append(m.group(0))
    return found
