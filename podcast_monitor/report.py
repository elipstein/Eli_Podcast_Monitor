"""Formats flagged episodes into the report output format."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .fetcher import Episode
from .matcher import FlagResult


@dataclass
class FlaggedEpisode:
    episode: Episode
    result: FlagResult


def _fmt_date(dt: datetime | None) -> str:
    return dt.strftime("%Y-%m-%d") if dt else "Unknown"


def to_markdown(flagged: list[FlaggedEpisode]) -> str:
    if not flagged:
        return "No episodes matched the Middle Eastern / Israeli cuisine criteria in this scan.\n"

    lines = []
    for f in sorted(flagged, key=lambda x: x.episode.published or datetime.min.replace(tzinfo=None), reverse=True):
        ep, res = f.episode, f.result
        keywords = ", ".join(sorted({m.text for m in res.matched_keywords}))
        lines.append(f"## {ep.title}")
        lines.append(f"- **Podcast:** {ep.podcast_name}")
        lines.append(f"- **Release date:** {_fmt_date(ep.published)}")
        lines.append(f"- **Matched keywords:** {keywords}")
        lines.append(f"- **Reason for flag:** {res.reason}")
        lines.append(f"- **Confidence:** {res.confidence}")
        if ep.link:
            lines.append(f"- **Link:** {ep.link}")
        lines.append("")
    return "\n".join(lines)


def to_dicts(flagged: list[FlaggedEpisode]) -> list[dict]:
    out = []
    for f in flagged:
        ep, res = f.episode, f.result
        out.append(
            {
                "podcast_name": ep.podcast_name,
                "episode_title": ep.title,
                "release_date": _fmt_date(ep.published),
                "matched_keywords": sorted({m.text for m in res.matched_keywords}),
                "reason_for_flag": res.reason,
                "confidence": res.confidence,
                "link": ep.link,
            }
        )
    return out
