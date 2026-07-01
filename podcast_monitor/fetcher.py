"""Fetches podcast episodes from RSS feeds."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import feedparser


@dataclass
class Episode:
    podcast_name: str
    title: str
    description: str
    published: datetime | None
    link: str


def _parsed_time_to_dt(parsed_time) -> datetime | None:
    if not parsed_time:
        return None
    return datetime(*parsed_time[:6], tzinfo=timezone.utc)


def fetch_episodes(podcast_name: str, feed_url: str) -> list[Episode]:
    """Fetch and parse all episodes from a single RSS feed URL.

    Raises no exception on network/parse failure; feedparser sets
    `bozo` and we surface that via an empty list plus the caller can
    inspect `feedparser.parse(...).bozo_exception` if needed.
    """
    parsed = feedparser.parse(feed_url)
    episodes = []
    for entry in parsed.entries:
        episodes.append(
            Episode(
                podcast_name=podcast_name,
                title=entry.get("title", ""),
                description=entry.get("summary", "") or entry.get("description", ""),
                published=_parsed_time_to_dt(entry.get("published_parsed")),
                link=entry.get("link", ""),
            )
        )
    return episodes


def fetch_all(podcasts: dict[str, str]) -> list[Episode]:
    """podcasts: mapping of podcast display name -> RSS feed URL."""
    all_episodes: list[Episode] = []
    for name, url in podcasts.items():
        all_episodes.extend(fetch_episodes(name, url))
    return all_episodes
