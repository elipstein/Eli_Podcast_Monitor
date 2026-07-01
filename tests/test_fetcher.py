from pathlib import Path

from podcast_monitor.fetcher import fetch_episodes

FIXTURE = Path(__file__).parent / "fixtures" / "sample_feed.xml"


def test_fetch_episodes_from_local_feed():
    episodes = fetch_episodes("Sample Food Podcast", FIXTURE.as_uri())
    assert len(episodes) == 5
    titles = {ep.title for ep in episodes}
    assert "Chef Interview: Michael Solomonov on Zahav and Israeli Cuisine" in titles
    first = episodes[0]
    assert first.podcast_name == "Sample Food Podcast"
    assert first.published is not None
