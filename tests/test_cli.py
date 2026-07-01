from pathlib import Path

from podcast_monitor.cli import scan
from podcast_monitor.report import to_dicts, to_markdown

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
