"""CLI entrypoint: scan configured podcasts and write a report of
flagged episodes.

Usage:
    python -m podcast_monitor.cli --config podcasts.yaml \
        --days 30 --format markdown --output reports/latest.md
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from .fetcher import fetch_episodes
from .matcher import evaluate
from .report import FlaggedEpisode, to_dicts, to_html, to_markdown


def load_podcasts(config_path: str) -> dict[str, str]:
    with open(config_path) as f:
        data = yaml.safe_load(f) or {}
    podcasts = {}
    for p in data.get("podcasts", []):
        if not p.get("feed_url"):
            print(f"skipping '{p['name']}': no feed_url configured yet", file=sys.stderr)
            continue
        podcasts[p["name"]] = p["feed_url"]
    return podcasts


def scan(podcasts: dict[str, str], since_days: int | None) -> list[FlaggedEpisode]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=since_days) if since_days else None
    flagged: list[FlaggedEpisode] = []
    for name, url in podcasts.items():
        try:
            episodes = fetch_episodes(name, url)
        except Exception as exc:  # noqa: BLE001 - one bad feed shouldn't stop the scan
            print(f"warning: failed to fetch '{name}' ({url}): {exc}", file=sys.stderr)
            continue
        for ep in episodes:
            if cutoff and ep.published and ep.published < cutoff:
                continue
            result = evaluate(ep.title, ep.description)
            if result.flagged:
                flagged.append(FlaggedEpisode(episode=ep, result=result))
    return flagged


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="podcasts.yaml", help="Path to podcasts.yaml")
    parser.add_argument("--days", type=int, default=30, help="Only consider episodes published in the last N days (0 = no limit)")
    parser.add_argument("--format", choices=["markdown", "json", "html"], default="markdown")
    parser.add_argument("--output", default=None, help="Write report to this file instead of stdout")
    parser.add_argument("--note", default="", help="Optional note shown at the top of the HTML report")
    args = parser.parse_args(argv)

    podcasts = load_podcasts(args.config)
    if not podcasts:
        print(f"No podcasts configured in {args.config}", file=sys.stderr)
        return 1

    flagged = scan(podcasts, since_days=args.days or None)

    if args.format == "markdown":
        output = to_markdown(flagged)
    elif args.format == "html":
        output = to_html(flagged, note=args.note)
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
