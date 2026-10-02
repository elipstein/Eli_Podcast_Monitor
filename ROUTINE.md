# Podcast Monitor Routine

How to run Eli's podcast scan manually, in a Claude Code session, instead
of via GitHub Actions. Invoke this whenever Eli asks to "run the podcast
monitor," "scan podcasts," or similar -- or periodically if he asks for a
recurring check-in (see **Scheduling** below for why that isn't fully
automatic).

This replaces three former GitHub Actions workflows
(`monitor.yml`, `profile_monitor.yml`, `pages.yml`), deleted when this
routine was written, because running it in-session means:
- No `ANTHROPIC_API_KEY` repo secret needed -- the taste-profile judgment
  step is done by Claude reasoning directly, not an API call.
- No GitHub Pages "Source" misconfiguration risk -- see **One-time setup**.

## Prerequisites (one-time)

1. `pip install -r requirements.txt` (feedparser, PyYAML; anthropic/pydantic
   are also listed but unused by this manual routine -- they're only for
   `profile_cli.py`/`profile_judge.py`, kept as an optional scripted
   alternative if Eli ever wants real GitHub Actions automation again).
2. **GitHub Pages source**: go to the repo's Settings -> Pages -> "Build
   and deployment" -> Source, and set it to **"Deploy from a branch"**,
   branch = this repo's working branch, folder = **/docs**. (Previously
   this required "GitHub Actions" as the source, because `pages.yml` did
   the deploying. That workflow is gone now, so Pages needs to serve
   `docs/` directly from the branch instead.) This is a one-time manual
   step in the GitHub UI -- no API/tool here can change repo Settings.

## Step 1: Cuisine matches (keyword rules, fully scripted)

No judgment needed -- just run the existing CLI:

```bash
python -m podcast_monitor.cli --config podcasts.yaml --days 14 \
    --format markdown --output "reports/$(date -u +%Y-%m-%d).md"
python -m podcast_monitor.cli --config podcasts.yaml --days 60 \
    --format html --output docs/index.html
```

## Step 2: Taste-profile picks (Claude judges inline, no API call)

**2a. Fetch candidate episodes:**

```bash
python -m podcast_monitor.profile_fetch --config profile_podcasts.yaml --days 14 > /tmp/profile_episodes.jsonl
```

Each line is `{"podcast_name", "title", "description", "published", "link"}`.

**2b. Judge each episode** by reading `PROFILE.md` and reasoning about fit,
the same way `profile_judge.py`'s system prompt frames it: *be selective --
most episodes of a show Eli already likes still aren't worth a special
recommendation; flag only the unusually good, timely, or distinctive ones,
or ones featuring someone Eli's specifically said he likes hearing from.*
For each row, add three fields: `fits` (bool), `confidence`
("High"/"Medium"/"Low"), `reasoning` (one or two sentences). Write the
augmented rows to a new JSONL file, e.g. `/tmp/profile_judged.jsonl`.

**2c. Render the report:**

```bash
python -m podcast_monitor.profile_report --input /tmp/profile_judged.jsonl \
    --format markdown --output "reports/profile-$(date -u +%Y-%m-%d).md"
python -m podcast_monitor.profile_report --input /tmp/profile_judged.jsonl \
    --format html --output docs/profile.html
```

## Step 3: Commit and push

```bash
git add reports/ docs/
git commit -m "Podcast scan: $(date -u +%Y-%m-%d)"
git push
```

GitHub Pages picks up the new `docs/` content automatically within a
minute or two (per the one-time Settings change above) -- no further
action needed.

## Step 4: Tell Eli what was found

Summarize newly-flagged episodes from both reports in chat -- don't make
him read the raw files unless he asks.

## Scheduling

There's no durable way to make this fire on its own from inside a Claude
session: `CronCreate` jobs are session-scoped, gone the moment this
session ends, and auto-expire after 7 days even if the session stays
open. That's materially weaker than GitHub Actions' server-side cron,
which is exactly what this routine replaced. Practically, that means:

- **Default:** run this routine on demand, whenever Eli asks.
- **If Eli wants it to actually recur unattended**, the honest options
  are (a) re-add a GitHub Actions workflow for part or all of it (trading
  back the Pages-source and `ANTHROPIC_API_KEY` friction this routine
  avoided), or (b) some durable scheduler outside this session's
  lifetime (a `/loop` kept running by Eli, an external cron hitting a
  webhook, etc.). Don't silently set up a `CronCreate` job and imply it's
  "automated now" -- it will quietly stop firing and nobody will notice
  until Eli asks why the site is stale.
