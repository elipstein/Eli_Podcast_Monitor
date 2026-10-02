"""Fetches recent episodes from profile_podcasts.yaml for a Claude Code
session to judge inline against PROFILE.md -- the fetch half of the
taste-profile routine (see ROUTINE.md). Deterministic and offline aside
from the feed fetches themselves; no Anthropic API call here.

Usage:
    python -m podcast_monitor.profile_fetch --config profile_podcasts.yaml --days 14

Prints one JSON object per line (JSONL): podcast_name, title, description,
published (ISO 8601 or null), link.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone

from .fetcher import fetch_episodes
from .profile_cli import load_podcasts


def fetch_all(podcasts: dict[str, str], since_days: int | None) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=since_days) if since_days else None
    out = []
    for name, url in podcasts.items():
        try:
            episodes = fetch_episodes(name, url)
        except Exception as exc:  # noqa: BLE001 - one bad feed shouldn't stop the fetch
            print(f"warning: failed to fetch '{name}' ({url}): {exc}", file=sys.stderr)
            continue
        for ep in episodes:
            if cutoff and ep.published and ep.published < cutoff:
                continue
            out.append(
                {
                    "podcast_name": ep.podcast_name,
                    "title": ep.title,
                    "description": ep.description,
                    "published": ep.published.isoformat() if ep.published else None,
                    "link": ep.link,
                }
            )
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="profile_podcasts.yaml")
    parser.add_argument("--days", type=int, default=14, help="0 = no date limit")
    args = parser.parse_args(argv)

    podcasts = load_podcasts(args.config)
    if not podcasts:
        print(f"No podcasts configured in {args.config}", file=sys.stderr)
        return 1

    for row in fetch_all(podcasts, since_days=args.days or None):
        print(json.dumps(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
