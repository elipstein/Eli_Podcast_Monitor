"""CLI entrypoint: scan Eli's broader-taste podcasts (profile_podcasts.yaml)
and flag episodes using Claude's judgment against PROFILE.md, instead of
the fixed keyword-combination rules used for the Middle Eastern / Israeli
cuisine matcher (see cli.py / matcher.py).

Usage:
    python -m podcast_monitor.profile_cli --config profile_podcasts.yaml \
        --days 14 --format markdown --output reports/profile_latest.md

Requires ANTHROPIC_API_KEY in the environment.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import anthropic
import yaml

from .fetcher import fetch_episodes
from .matcher import FlagResult
from .profile_judge import judge_episode, load_profile
from .report import FlaggedEpisode, to_dicts, to_html, to_markdown

NAV_HTML = (
    '<nav class="site-nav">'
    '<a href="index.html">Cuisine matches</a>'
    '<a href="profile.html" class="active">Taste-profile picks</a>'
    "</nav>"
)


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


def scan(
    client: anthropic.Anthropic,
    podcasts: dict[str, str],
    profile_text: str,
    since_days: int | None,
) -> list[FlaggedEpisode]:
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
            judgment = judge_episode(client, profile_text, ep.podcast_name, ep.title, ep.description)
            if judgment.fits:
                result = FlagResult(
                    flagged=True,
                    matched_keywords=[],
                    fired_rules=["profile_judgment"],
                    confidence=judgment.confidence,
                    reason=judgment.reasoning,
                )
                flagged.append(FlaggedEpisode(episode=ep, result=result))
    return flagged


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="profile_podcasts.yaml", help="Path to profile_podcasts.yaml")
    parser.add_argument("--days", type=int, default=14, help="Only consider episodes published in the last N days (0 = no limit)")
    parser.add_argument("--format", choices=["markdown", "json", "html"], default="markdown")
    parser.add_argument("--output", default=None, help="Write report to this file instead of stdout")
    parser.add_argument("--note", default="", help="Optional note shown at the bottom of the HTML report")
    args = parser.parse_args(argv)

    podcasts = load_podcasts(args.config)
    if not podcasts:
        print(f"No podcasts configured in {args.config}", file=sys.stderr)
        return 1

    client = anthropic.Anthropic()  # resolves ANTHROPIC_API_KEY from the environment
    profile_text = load_profile()

    flagged = scan(client, podcasts, profile_text, since_days=args.days or None)

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
