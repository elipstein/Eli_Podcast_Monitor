# Eli Podcast Monitor

Scans podcast RSS feeds for episodes about Middle Eastern / Israeli
cuisine, chef interviews, and behind-the-scenes kitchen/restaurant
stories, and flags the ones that match.

## How flagging works

`podcast_monitor/keywords.py` holds four keyword categories (chef
names, cuisine terms, ingredients/dishes, behind-the-scenes signal
phrases) and five combination rules — an episode is flagged if its
title + description contain keywords satisfying any one of:

1. Chef interview + Middle Eastern / Israeli cuisine
2. Ingredient deep dive + Levantine origin
3. Restaurant story + Israeli/Mizrahi/Levantine chef
4. Cultural or historical food narrative + Levant region
5. Behind-the-scenes kitchen talk + relevant chef or dish keyword

Confidence is `High` when 2+ rules fire (or a named chef appears
alongside a cuisine term), `Medium` when a named chef or a strong
cuisine/ingredient match backs a single rule, and `Low` otherwise.

Edit `podcast_monitor/keywords.py` to add chefs, ingredients, or
signal phrases as you discover more.

## Podcasts monitored

`podcasts.yaml` is a starting list of food/chef/Jewish-and-Middle-
Eastern-food-culture shows. **There is no "all podcasts" feed** — you
tell it which shows to watch by adding `{name, feed_url}` entries.
Some entries have `feed_url: null` because their RSS URL couldn't be
confirmed from this dev environment (see note in the file) — resolve
those via a podcast app's "copy RSS link" feature or a tool like
https://rss.com/tools/find-my-feed/ before they'll be scanned.

## Usage

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Scan episodes published in the last 30 days, print a Markdown report
python -m podcast_monitor.cli --config podcasts.yaml --days 30

# JSON output to a file, no date filter
python -m podcast_monitor.cli --config podcasts.yaml --days 0 --format json --output reports/latest.json
```

Report fields per flagged episode: podcast name, episode title,
release date, matched keywords, reason for flag, confidence level.

## Automated weekly scans

`.github/workflows/monitor.yml` runs the scan every Monday (and on
manual dispatch), commits the report to `reports/`, and opens a GitHub
issue listing flagged episodes. It runs on a GitHub-hosted runner with
normal internet access, so it can reach podcast RSS hosts that this
dev sandbox could not.

## Tests

```bash
pip install -r requirements.txt pytest
pytest
```

Tests run entirely offline against a local RSS fixture
(`tests/fixtures/sample_feed.xml`) — no network required.

## Known limitation

This tool was built and tested inside a sandboxed session whose
outbound network access is restricted to an allowlist (pypi, npm,
github, anthropic) and does not include podcast hosting CDNs
(Megaphone, Acast, Omny, etc.). The matching engine and CLI are fully
tested against local fixtures, but no live feed in `podcasts.yaml` was
fetch-verified from this session — do that once from an unrestricted
network (your machine, or the GitHub Actions workflow) before trusting
the configured `feed_url` values.
