# Eli Podcast Monitor

Scans podcast RSS feeds for episodes about Middle Eastern / Israeli
cuisine, chef interviews, and behind-the-scenes kitchen/restaurant
stories, and flags the ones that match.

See [`PROFILE.md`](PROFILE.md) for the broader picture: everything
Eli's said he subscribes to (not just food shows), what that implies
about his taste, and podcast/episode recommendations that go beyond
the strict Middle-Eastern-cuisine rule engine below.

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

`OTHER_FAVORITE_CHEFS` in `keywords.py` holds people Eli wants flagged
in a chef-interview context regardless of region/cuisine: Will
Guidara, Danny Meyer, Michael Solomonov, and (found while researching
Eli's "Think & Drink Different") Jeremy Fogel and chef Asaf Doktor,
who co-host כאן's culinary-history documentary on the ancient
Levantine/Israelite diet.

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
without a separate cuisine-term match. `ACHOREI_HATZLACHAT_GUESTS` is
complete (Eli supplied the full 14-episode list); `LASHEVET_LAKACHAT_GUESTS`
was built from web search and covers roughly episodes 1-51, not
exhaustive — add names as new episodes/guests turn up. A natural
follow-up would be a small script that parses these shows' own RSS
feeds (episode titles follow consistent "פרק N: ... - <guest>"
patterns) to grow the lists automatically.

## Taste-profile pipeline (LLM judgment, not keywords)

`podcast_monitor/profile_cli.py` is a second, separate pipeline for
everything in [`PROFILE.md`](PROFILE.md) that isn't Middle Eastern
cuisine — general shows Eli's taste implies he'd like. There's no
keyword combination that captures "would Eli like this episode of
Acquired," so instead of `matcher.py`'s fixed rules, `profile_judge.py`
sends each episode's title + description to Claude (`claude-opus-4-8`)
alongside the full text of `PROFILE.md` and asks for a structured
verdict — `fits: bool`, `confidence`, `reasoning` — via
`client.messages.parse(..., output_format=EpisodeJudgment)` (a Pydantic
model). It's deliberately selective: most episodes of a show Eli
already likes still shouldn't be flagged, only the unusually good,
timely, or distinctive ones.

`profile_podcasts.yaml` is the starter show list, one per theme from
`PROFILE.md`'s recommendations (Huberman Lab, The Prof G Pod, This
American Life, Wondering Jews with Mijal and Noam) — add more from
`PROFILE.md` or elsewhere.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python -m podcast_monitor.profile_cli --config profile_podcasts.yaml --days 14
```

**This requires an `ANTHROPIC_API_KEY`, which this dev sandbox does not
have** — the pipeline's surrounding logic (config loading, date
filtering, report rendering) is unit-tested with a mocked Anthropic
client (`tests/test_profile.py`), but the actual API call has not been
exercised against the live API from this session. For the automated
version, add `ANTHROPIC_API_KEY` as a repo secret (**Settings → Secrets
and variables → Actions**) — `.github/workflows/profile_monitor.yml`
checks for it and skips with a warning if it's missing, otherwise runs
weekly and updates `docs/profile.html`.

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
guest lists (above) feed the matcher. Four shows discovered via web
search — אנזל ולוקסי, Yuvi Yam | קולינריה בישראל, אוכל ישראל עם גיל
חובב, and מקורב לצלחת (Dishing Out) — were added to the monitored list
instead, since Eli doesn't already listen to those.

Also **not monitored, and never to be re-suggested**: general-interest
shows Eli already subscribes to that mostly fall outside this
project's scope entirely (Sam Harris, Rhonda Patrick, Bill Maher,
Pivot, השבוע - פודקאסט הארץ, The Moth, This Is TASTE, And Here's Modi,
The Daily Churn, Think & Drink Different, Absolutely Mental) — see the
comment block at the top of `podcasts.yaml` for the full list and
reasoning.

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

Two independent GitHub Actions workflows, offset by 15 minutes so they
don't race on `docs/`:

- `.github/workflows/monitor.yml` — the cuisine keyword-rule scan.
  Runs every Monday 13:00 UTC (and on manual dispatch), commits the
  report to `reports/`, updates `docs/index.html`, and opens a GitHub
  issue listing flagged episodes.
- `.github/workflows/profile_monitor.yml` — the taste-profile LLM scan.
  Runs every Monday 13:15 UTC, same behavior, updates `docs/profile.html`.
  Requires the `ANTHROPIC_API_KEY` repo secret (see above) — skips with
  a warning if it's not set.

Both run on GitHub-hosted runners with normal internet access, so they
can reach podcast RSS hosts that this dev sandbox could not.

## Website

`docs/index.html` (cuisine matches) and `docs/profile.html`
(taste-profile picks) are static HTML reports, cross-linked by a nav
bar, meant to be served by GitHub Pages at
**https://elipstein.github.io/Eli_Podcast_Monitor/**. `index.html`
currently holds a manually-researched snapshot of matching episodes
(dates marked "Unknown" couldn't be confirmed); `profile.html` is an
honest empty placeholder, since generating it for real requires the
`ANTHROPIC_API_KEY` this sandbox doesn't have. The weekly scans replace
both with live results once feeds and the API key are in place.

**One-time setup (do this in the GitHub UI, not something this repo
can do on its own):** go to the repo's **Settings → Pages**, and under
"Build and deployment" set **Source: GitHub Actions**. After that,
`.github/workflows/pages.yml` deploys `docs/` automatically on every
push and the site goes live at the URL above within a minute or two.
Regenerate the pages locally with:

```bash
python -m podcast_monitor.cli --config podcasts.yaml --days 60 --format html --output docs/index.html
python -m podcast_monitor.profile_cli --config profile_podcasts.yaml --days 60 --format html --output docs/profile.html
```

## Tests

```bash
pip install -r requirements.txt pytest
pytest
```

Tests run entirely offline against a local RSS fixture
(`tests/fixtures/sample_feed.xml`) — no network required. The
taste-profile pipeline's tests mock the Anthropic client
(`tests/test_profile.py`), so they don't need `ANTHROPIC_API_KEY` either.

## Known limitations

This tool was built and tested inside a sandboxed session whose
outbound network access is restricted to an allowlist (pypi, npm,
github, anthropic) and does not include podcast hosting CDNs
(Megaphone, Acast, Omny, etc.). The matching engine and CLI are fully
tested against local fixtures, but no live feed in `podcasts.yaml` or
`profile_podcasts.yaml` was fetch-verified from this session — do that
once from an unrestricted network (your machine, or the GitHub Actions
workflow) before trusting the configured `feed_url` values.

Separately, this session has no `ANTHROPIC_API_KEY`, so
`profile_cli.py`'s actual call to Claude has never run for real —
only its surrounding logic, via a mocked client. Run it once with a
real key (locally, or via the `profile_monitor.yml` workflow once the
secret is added) to confirm the live behavior matches what the tests
predict.
