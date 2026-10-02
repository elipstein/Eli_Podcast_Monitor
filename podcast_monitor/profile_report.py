"""Renders judged taste-profile episodes into a report -- the render half
of the taste-profile routine (see ROUTINE.md). Takes the JSONL that
profile_fetch.py produced, after a Claude Code session has added
"fits"/"confidence"/"reasoning" to each row by judging it against
PROFILE.md inline (no Anthropic API call in this script either).

Usage:
    python -m podcast_monitor.profile_report --input judged.jsonl \
        --format html --output docs/profile.html

Each input line must be a JSON object with: podcast_name, title,
description, published (ISO 8601 or null), link, fits (bool),
confidence ("High"/"Medium"/"Low"), reasoning (str). Rows with
fits=false are dropped.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from .fetcher import Episode
from .matcher import FlagResult
from .profile_cli import NAV_HTML
from .report import FlaggedEpisode, to_dicts, to_html, to_markdown


def load_judged(path: str) -> list[FlaggedEpisode]:
    flagged = []
    with open(path) as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if not row.get("fits"):
                continue
            published = datetime.fromisoformat(row["published"]) if row.get("published") else None
            ep = Episode(
                podcast_name=row["podcast_name"],
                title=row["title"],
                description=row.get("description", ""),
                published=published,
                link=row.get("link"),
            )
            result = FlagResult(
                flagged=True,
                matched_keywords=[],
                fired_rules=["profile_judgment"],
                confidence=row.get("confidence", "Low"),
                reason=row.get("reasoning", ""),
            )
            flagged.append(FlaggedEpisode(episode=ep, result=result))
    return flagged


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="JSONL file of judged episodes")
    parser.add_argument("--format", choices=["markdown", "json", "html"], default="html")
    parser.add_argument("--output", default=None)
    parser.add_argument("--note", default="")
    args = parser.parse_args(argv)

    flagged = load_judged(args.input)

    if args.format == "markdown":
        output = to_markdown(flagged)
    elif args.format == "html":
        output = to_html(
            flagged,
            note=args.note,
            page_title="Eli Podcast Monitor -- Taste-Profile Picks",
            eyebrow="Podcast monitor",
            page_h1="Taste-Profile Picks",
            page_subtitle="Episodes Claude judged as a good fit for Eli's broader listening profile (PROFILE.md) -- not keyword-matched.",
            nav=NAV_HTML,
        )
    else:
        output = json.dumps(to_dicts(flagged), indent=2)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Wrote {len(flagged)} flagged episode(s) to {args.output}")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
