from datetime import datetime, timezone
from pathlib import Path

from podcast_monitor.fetcher import Episode
from podcast_monitor.matcher import evaluate
from podcast_monitor.cli import scan
from podcast_monitor.report import FlaggedEpisode, to_dicts, to_html, to_markdown

FIXTURE = Path(__file__).parent / "fixtures" / "sample_feed.xml"


def test_scan_flags_expected_episodes():
    podcasts = {"Sample Food Podcast": FIXTURE.as_uri()}
    flagged = scan(podcasts, since_days=None)
    titles = {f.episode.title for f in flagged}
    assert "Chef Interview: Michael Solomonov on Zahav and Israeli Cuisine" in titles
    assert "The History of Sumac and Za'atar" in titles
    assert "Restaurant Opening Diaries: A New Mizrahi Spot" in titles
    assert "Diaspora Cooking: Palestinian Food Anthropology" in titles
    assert "Our Favorite Pasta Sauces" not in titles
    assert len(flagged) == 4


def test_report_formats_render_without_error():
    podcasts = {"Sample Food Podcast": FIXTURE.as_uri()}
    flagged = scan(podcasts, since_days=None)
    md = to_markdown(flagged)
    assert "Michael Solomonov" in md
    assert "Confidence" in md
    rows = to_dicts(flagged)
    assert len(rows) == 4
    assert all(r["confidence"] in {"High", "Medium", "Low"} for r in rows)

    html = to_html(flagged)
    assert "<html" in html
    assert "Michael Solomonov" in html
    assert html.count('class="card"') == 4


def test_sorting_handles_episodes_with_missing_publish_date():
    # feedparser entries with no pubDate leave Episode.published as None,
    # which must sort safely alongside timezone-aware dates from other entries.
    with_date = Episode(
        podcast_name="P",
        title="Chef Interview with Michael Solomonov",
        description="A chef interview about Israeli cuisine.",
        published=datetime(2026, 1, 1, tzinfo=timezone.utc),
        link="",
    )
    without_date = Episode(
        podcast_name="P",
        title="Chef Interview with Reem Assil",
        description="A chef interview about Israeli cuisine.",
        published=None,
        link="",
    )
    flagged = [
        FlaggedEpisode(episode=with_date, result=evaluate(with_date.title, with_date.description)),
        FlaggedEpisode(episode=without_date, result=evaluate(without_date.title, without_date.description)),
    ]
    md = to_markdown(flagged)
    html = to_html(flagged)
    assert "Unknown" in md
    assert "Reem Assil" in html and "Solomonov" in html
