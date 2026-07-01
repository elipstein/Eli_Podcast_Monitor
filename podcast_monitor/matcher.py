"""Matching engine: scans episode text for keywords and applies the
five flagging combination rules to decide whether an episode should
be flagged, and with what confidence."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .keywords import ALL_KEYWORDS, Category, RULES, CHEF_NAMES, INGREDIENT_TERMS

_WORD_BOUNDARY_SAFE = re.compile(r"[a-z0-9']+")


def _normalize(text: str) -> str:
    return text.lower()


def _contains(haystack: str, needle: str) -> bool:
    """Substring match on normalized text. Multi-word keywords (chef
    names, phrases) are matched as plain substrings; single tokens use
    word boundaries to avoid matching inside unrelated words."""
    needle = needle.lower()
    if " " in needle or "'" in needle:
        return needle in haystack
    return re.search(rf"\b{re.escape(needle)}\b", haystack) is not None


@dataclass
class MatchedKeyword:
    text: str
    category: Category


@dataclass
class FlagResult:
    flagged: bool
    matched_keywords: list[MatchedKeyword] = field(default_factory=list)
    fired_rules: list[str] = field(default_factory=list)
    confidence: str = "Low"
    reason: str = ""


def find_keywords(text: str) -> list[MatchedKeyword]:
    normalized = _normalize(text)
    found = []
    for keyword, category in ALL_KEYWORDS.items():
        if _contains(normalized, keyword):
            found.append(MatchedKeyword(text=keyword, category=category))
    return found


def evaluate(title: str, description: str = "") -> FlagResult:
    """Evaluate an episode's title + description against the flagging
    rules and return whether it should be flagged, with matched
    keywords, which rules fired, and a confidence level."""
    text = f"{title}\n{description}"
    matches = find_keywords(text)
    matched_lower = {m.text.lower() for m in matches}
    by_category = {c: {m.text.lower() for m in matches if m.category == c} for c in Category}

    def _side_hit(explicit: set[str], categories: set[Category]) -> bool:
        if explicit and (explicit & matched_lower):
            return True
        return any(by_category.get(c) for c in categories)

    fired = []
    for rule in RULES:
        if _side_hit(rule.left, rule.left_categories) and _side_hit(rule.right, rule.right_categories):
            fired.append(rule)

    if not fired:
        return FlagResult(flagged=False, matched_keywords=matches)

    has_named_chef = bool(by_category[Category.CHEF])
    if len(fired) >= 2 or (has_named_chef and len(fired) >= 1 and by_category[Category.CUISINE]):
        confidence = "High"
    elif has_named_chef or len(fired) >= 1 and (by_category[Category.CUISINE] or by_category[Category.INGREDIENT]):
        confidence = "Medium"
    else:
        confidence = "Low"

    reason = "; ".join(rule.description for rule in fired)

    return FlagResult(
        flagged=True,
        matched_keywords=matches,
        fired_rules=[r.id for r in fired],
        confidence=confidence,
        reason=reason,
    )
