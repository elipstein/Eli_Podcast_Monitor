# Eli Podcast Monitor

Scans podcast RSS feeds for episodes about Middle Eastern / Israeli
cuisine, chef interviews, and behind-the-scenes kitchen/restaurant
stories, and flags the ones that match.

See [`PROFILE.md`](PROFILE.md) for the broader picture: everything
Eli's said he subscribes to (not just food shows), what that implies
about his taste, and podcast/episode recommendations that go beyond
the strict Middle-Eastern-cuisine rule engine below.

**There's no automated scanning anymore.** See [`ROUTINE.md`](ROUTINE.md)
for the manual routine to run in a Claude Code session instead — it
replaced the three GitHub Actions workflows this repo used to have.

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

Everything in [`PROFILE.md`](PROFILE.md) that isn't Middle Eastern
cuisine — general shows Eli's taste implies he'd like — gets a second,
separate matching approach. There's no keyword combination that
captures "would Eli like this episode of Acquired," so instead of
`matcher.py`'s fixed rules, each episode gets judged against the full
text of `PROFILE.md` in free text: `fits: bool`, `confidence`,
`reasoning`. It's deliberately selective — most episodes of a show Eli
already likes still shouldn't be flagged, only the unusually good,
timely, or distinctive ones.

**The default way to run this is [`ROUTINE.md`](ROUTINE.md) Step 2**:
`profile_fetch.py` fetches candidate episodes as plain JSON, a Claude
Code session reads `PROFILE.md` and judges each one inline (no API
call, no `ANTHROPIC_API_KEY` needed), and `profile_report.py` renders
the judged results. This is what replaced the old
`profile_monitor.yml` GitHub Actions workflow.

There's also a **scripted, fully-automated alternative** —
`profile_judge.py` / `profile_cli.py` — that calls the Claude API
directly via `client.messages.parse(..., output_format=EpisodeJudgment)`
(a Pydantic model, model `claude-opus-4-8`) instead of relying on an
in-session Claude to judge. It's unused by the current routine but
kept in case Eli wants real unattended automation again later (e.g. a
re-added GitHub Actions workflow) — that path needs an
`ANTHROPIC_API_KEY`, which this dev sandbox never had, so only its
surrounding logic (config loading, date filtering, report rendering)
is verified, via a mocked Anthropic client (`tests/test_profile.py`).

`profile_podcasts.yaml` is the starter show list, one per theme from
`PROFILE.md`'s recommendations (Huberman Lab, The Prof G Pod, This
American Life, Wondering Jews with Mijal and Noam) — add more from
`PROFILE.md` or elsewhere.

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

There aren't any anymore — this used to run via two GitHub Actions
workflows (`monitor.yml`, `profile_monitor.yml`) plus a `pages.yml`
deploy workflow, all deleted. See [`ROUTINE.md`](ROUTINE.md) for the
manual replacement and why it isn't (and can't safely be) turned back
into unattended automation from inside a Claude session.

## Website

`docs/index.html` (cuisine matches) and `docs/profile.html`
(taste-profile picks) are static HTML reports, cross-linked by a nav
bar, meant to be served by GitHub Pages at
**https://elipstein.github.io/Eli_Podcast_Monitor/**. `index.html`
currently holds a manually-researched snapshot of matching episodes
(dates marked "Unknown" couldn't be confirmed); `profile.html` is an
honest empty placeholder, since generating it for real means running
[`ROUTINE.md`](ROUTINE.md) Step 2. Re-running the routine replaces both
with current results.

**One-time setup (do this in the GitHub UI, not something this repo
can do on its own):** go to the repo's **Settings → Pages**, and under
"Build and deployment" set **Source: Deploy from a branch**, branch =
this repo's working branch, folder = **/docs**. (This is different from
when `pages.yml` existed, which needed Source set to "GitHub Actions"
instead — now that there's no deploy workflow, Pages needs to serve
`docs/` directly from the branch.) After that, the site goes live at
the URL above within a minute or two of any push that touches `docs/`.
Regenerate the pages locally with:

```bash
python -m podcast_monitor.cli --config podcasts.yaml --days 60 --format html --output docs/index.html
# docs/profile.html: see ROUTINE.md Step 2 (requires judging episodes inline, not a single command)
```

## Tests

```bash
pip install -r requirements.txt pytest
pytest
```

Tests run entirely offline against a local RSS fixture
(`tests/fixtures/sample_feed.xml`) — no network required. The
scripted `profile_cli.py`/`profile_judge.py` alternative's tests mock
the Anthropic client (`tests/test_profile.py`); the default
`profile_fetch.py`/`profile_report.py` routine needs no mocking at all
since it never calls an LLM itself (`tests/test_profile_routine.py`).

## Known limitations

This tool was built and tested inside a sandboxed session whose
outbound network access is restricted to an allowlist (pypi, npm,
github, anthropic) and does not include podcast hosting CDNs
(Megaphone, Acast, Omny, etc.). The matching engine and CLI are fully
tested against local fixtures, but no live feed in `podcasts.yaml` or
`profile_podcasts.yaml` was fetch-verified from this session — do that
once from an unrestricted network (your machine, or whenever
[`ROUTINE.md`](ROUTINE.md) is run) before trusting the configured
`feed_url` values.

Separately, this session has no `ANTHROPIC_API_KEY`, so
`profile_cli.py`/`profile_judge.py`'s actual call to Claude has never
run for real — only its surrounding logic, via a mocked client. That
path is optional now (see "Taste-profile pipeline" above) since the
default routine judges episodes in-session instead, but if it's ever
revived, run it once with a real key to confirm the live behavior
matches what the tests predict.
