from pathlib import Path
from unittest.mock import MagicMock

from podcast_monitor.fetcher import Episode
from podcast_monitor.profile_cli import scan
from podcast_monitor.profile_judge import EpisodeJudgment, judge_episode
from podcast_monitor.report import to_html, to_markdown

FIXTURE = Path(__file__).parent / "fixtures" / "sample_feed.xml"


def _mock_client(judgment: EpisodeJudgment) -> MagicMock:
    client = MagicMock()
    client.messages.parse.return_value = MagicMock(parsed_output=judgment)
    return client


def test_judge_episode_returns_parsed_output():
    judgment = EpisodeJudgment(fits=True, confidence="High", reasoning="Great fit.")
    client = _mock_client(judgment)

    result = judge_episode(client, "profile text", "Some Podcast", "Episode Title", "Description")

    assert result == judgment
    client.messages.parse.assert_called_once()
    kwargs = client.messages.parse.call_args.kwargs
    assert kwargs["model"] == "claude-opus-4-8"
    assert kwargs["output_format"] is EpisodeJudgment
    assert "profile text" in kwargs["system"]
    assert "Some Podcast" in kwargs["messages"][0]["content"]


def test_scan_flags_episodes_judged_as_fitting():
    judgment = EpisodeJudgment(fits=True, confidence="Medium", reasoning="Matches the taste profile.")
    client = _mock_client(judgment)
    podcasts = {"Sample Food Podcast": FIXTURE.as_uri()}

    flagged = scan(client, podcasts, "profile text", since_days=None)

    assert len(flagged) == 5  # every episode in the fixture, since the mock always says "fits"
    assert all(f.result.confidence == "Medium" for f in flagged)
    assert all(f.result.reason == "Matches the taste profile." for f in flagged)
    assert all(f.result.matched_keywords == [] for f in flagged)


def test_scan_skips_episodes_judged_as_not_fitting():
    judgment = EpisodeJudgment(fits=False, confidence="Low", reasoning="Not a fit.")
    client = _mock_client(judgment)
    podcasts = {"Sample Food Podcast": FIXTURE.as_uri()}

    flagged = scan(client, podcasts, "profile text", since_days=None)

    assert flagged == []


def test_profile_flagged_episode_renders_without_keywords_section():
    ep = Episode(podcast_name="P", title="T", description="D", published=None, link="https://example.com")
    from podcast_monitor.matcher import FlagResult
    from podcast_monitor.report import FlaggedEpisode

    result = FlagResult(flagged=True, matched_keywords=[], fired_rules=["profile_judgment"], confidence="High", reason="Great episode.")
    flagged = [FlaggedEpisode(episode=ep, result=result)]

    md = to_markdown(flagged)
    assert "Matched keywords" not in md
    assert "Great episode." in md

    html = to_html(flagged)
    assert "Matched keywords" not in html
    assert "Great episode." in html
