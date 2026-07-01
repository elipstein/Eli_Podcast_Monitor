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

### Hebrew support

Every keyword concept (chef names, cuisine terms, ingredients, signal
phrases) is stored as a list of surface forms across languages, and
`keywords.py` currently seeds both English and Hebrew forms. Hebrew
tokens are matched as plain substrings rather than with a `\b`
word-boundary regex, because Hebrew attaches prefixes like ה/ב/ל/מ/ו
directly with no space (e.g. "החומוס" — *the* hummus — still needs to
match the keyword "חומוס"); see `_contains` in `matcher.py`.

`LASHEVET_LAKACHAT_GUESTS` and `ACHOREI_HATZLACHAT_GUESTS` in
`keywords.py` are hand-seeded guest lists from two Hebrew
restaurant-industry podcasts Eli already listens to in full: לשבת
לקחת (hosts Nadav Bornstein & Kfir Arbiv) and מאחורי הצלחת עם גדי חן
(host Gadi Chen). Per Eli, *any* past guest of either show counts as a
chef he likes, so an episode naming one of them on **any other**
podcast, in Hebrew or English, will flag under rule 1, 3, or 5 even
without a separate cuisine-term match. Lists built from web search and
not exhaustive — add names as new episodes/guests turn up. A natural
follow-up would be a small script that parses these shows' own RSS
feeds (episode titles follow consistent "פרק N: ... - <guest>"
patterns) to grow the lists automatically.

## Podcasts monitored

`podcasts.yaml` is a starting list of food/chef/Jewish-and-Middle-
Eastern-food-culture shows. **There is no "all podcasts" feed** — you
tell it which shows to watch by adding `{name, feed_url}` entries.
Some entries have `feed_url: null` because their RSS URL couldn't be
confirmed from this dev environment (see note in the file) — resolve
those via a podcast app's "copy RSS link" feature or a tool like
https://rss.com/tools/find-my-feed/ before they'll be scanned.

**Deliberately not in this list:** לשבת לקחת, מדברים מהבטן, and
מאחורי הצלחת עם גדי חן. Eli listens to every episode of all three
already, so flagging their own episodes would be noise — only their
guest lists (above) feed the matcher. Three shows discovered via web
search *as similar to those three* — אנזל ולוקסי, Yuvi Yam | קולינריה
בישראל, and אוכל ישראל עם גיל חובב — were added to the monitored list
instead, since Eli doesn't already listen to those.

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

## Website

`docs/index.html` is a static HTML report (built with `--format html`)
meant to be served by GitHub Pages at
**https://elipstein.github.io/Eli_Podcast_Monitor/**. It currently
holds a manually-researched snapshot of matching episodes (dates
marked "Unknown" couldn't be confirmed) — the weekly scan will replace
it with live RSS results once `podcasts.yaml` has real feed URLs.

**One-time setup (do this in the GitHub UI, not something this repo
can do on its own):** go to the repo's **Settings → Pages**, and under
"Build and deployment" set **Source: GitHub Actions**. After that,
`.github/workflows/pages.yml` deploys `docs/` automatically on every
push and the site goes live at the URL above within a minute or two.
Regenerate the page locally with:

```bash
python -m podcast_monitor.cli --config podcasts.yaml --days 60 --format html --output docs/index.html
```

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
