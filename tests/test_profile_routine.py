import json
from pathlib import Path

from podcast_monitor.profile_fetch import fetch_all
from podcast_monitor.profile_report import load_judged

FIXTURE = Path(__file__).parent / "fixtures" / "sample_feed.xml"


def test_fetch_all_returns_plain_dicts_for_every_episode():
    podcasts = {"Sample Food Podcast": FIXTURE.as_uri()}

    rows = fetch_all(podcasts, since_days=None)

    assert len(rows) == 5
    assert all(set(row) == {"podcast_name", "title", "description", "published", "link"} for row in rows)
    assert all(row["podcast_name"] == "Sample Food Podcast" for row in rows)
    # JSON-serializable, since profile_fetch.main() prints these with json.dumps
    json.dumps(rows)


def test_load_judged_drops_non_fitting_rows_and_keeps_fitting_ones(tmp_path):
    judged_path = tmp_path / "judged.jsonl"
    judged_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "podcast_name": "P",
                        "title": "Fits",
                        "description": "D",
                        "published": "2026-01-01T00:00:00+00:00",
                        "link": "https://example.com/a",
                        "fits": True,
                        "confidence": "High",
                        "reasoning": "Great episode.",
                    }
                ),
                json.dumps(
                    {
                        "podcast_name": "P",
                        "title": "Does not fit",
                        "description": "D",
                        "published": None,
                        "link": None,
                        "fits": False,
                        "confidence": "Low",
                        "reasoning": "Not relevant.",
                    }
                ),
            ]
        )
    )

    flagged = load_judged(str(judged_path))

    assert len(flagged) == 1
    assert flagged[0].episode.title == "Fits"
    assert flagged[0].result.confidence == "High"
    assert flagged[0].result.reason == "Great episode."
    assert flagged[0].result.matched_keywords == []
