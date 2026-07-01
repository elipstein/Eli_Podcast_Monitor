"""Formats flagged episodes into the report output format.

Shared by both matching pipelines: the keyword-rule engine in matcher.py
(Middle Eastern / Israeli cuisine) and the LLM-judgment engine in
profile_judge.py (Eli's broader taste profile). The latter produces
FlagResult objects with empty matched_keywords -- the keywords section
renders only when there's something to show.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape

from .fetcher import Episode
from .matcher import FlagResult


@dataclass
class FlaggedEpisode:
    episode: Episode
    result: FlagResult


def _fmt_date(dt: datetime | None) -> str:
    return dt.strftime("%Y-%m-%d") if dt else "Unknown"


def to_markdown(flagged: list[FlaggedEpisode]) -> str:
    if not flagged:
        return "No episodes matched the criteria in this scan.\n"

    lines = []
    for f in sorted(flagged, key=lambda x: x.episode.published or datetime.min.replace(tzinfo=timezone.utc), reverse=True):
        ep, res = f.episode, f.result
        keywords = ", ".join(sorted({m.text for m in res.matched_keywords}))
        lines.append(f"## {ep.title}")
        lines.append(f"- **Podcast:** {ep.podcast_name}")
        lines.append(f"- **Release date:** {_fmt_date(ep.published)}")
        if keywords:
            lines.append(f"- **Matched keywords:** {keywords}")
        lines.append(f"- **Reason for flag:** {res.reason}")
        lines.append(f"- **Confidence:** {res.confidence}")
        if ep.link:
            lines.append(f"- **Link:** {ep.link}")
        lines.append("")
    return "\n".join(lines)


_CONFIDENCE_CLASS = {"High": "high", "Medium": "medium", "Low": "low"}

_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>
<style>
  :root {{ color-scheme: light dark; }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    max-width: 760px;
    margin: 0 auto;
    padding: 3rem 1.5rem 4rem;
    line-height: 1.55;
    color: #1c1c1e;
    background: #fafafa;
    -webkit-font-smoothing: antialiased;
  }}
  header {{ margin-bottom: 2.25rem; }}
  .eyebrow {{
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #8a6fd8;
    margin: 0 0 0.4rem;
  }}
  h1 {{ font-size: 1.75rem; margin: 0 0 0.4rem; letter-spacing: -0.01em; }}
  .subtitle {{ color: #666; font-size: 0.95rem; margin: 0.2rem 0; }}
  .meta-line {{ color: #999; font-size: 0.82rem; margin-top: 0.6rem; }}
  nav.site-nav {{ margin-top: 1rem; font-size: 0.85rem; }}
  nav.site-nav a {{
    display: inline-block;
    padding: 0.3rem 0.75rem;
    border: 1px solid #ddd;
    border-radius: 999px;
    margin-right: 0.5rem;
    text-decoration: none;
    color: #444;
  }}
  nav.site-nav a.active {{ background: #1c1c1e; color: #fff; border-color: #1c1c1e; }}
  .card {{
    background: #fff;
    border: 1px solid #e7e7e7;
    border-left: 4px solid #ddd;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
  }}
  .card.conf-high {{ border-left-color: #2f9e52; }}
  .card.conf-medium {{ border-left-color: #d1980a; }}
  .card.conf-low {{ border-left-color: #999; }}
  .card-head {{ display: flex; align-items: flex-start; gap: 0.7rem; margin-bottom: 0.6rem; }}
  .avatar {{
    flex: 0 0 auto;
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    background: #efe9fc;
    color: #6a4fc2;
    font-weight: 700;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 0.1rem;
  }}
  .card h2 {{ font-size: 1.08rem; margin: 0 0 0.15rem; line-height: 1.35; }}
  .podcast-name {{ font-size: 0.82rem; color: #888; }}
  .meta {{ font-size: 0.88rem; color: #444; margin: 0.3rem 0; }}
  .meta strong {{ color: #111; font-weight: 600; }}
  .badge {{
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.15rem 0.6rem;
    border-radius: 999px;
    margin-left: 0.35rem;
    letter-spacing: 0.02em;
  }}
  .badge.high {{ background: #e2f6e7; color: #1a7431; }}
  .badge.medium {{ background: #fdf1d6; color: #8a5a00; }}
  .badge.low {{ background: #eee; color: #555; }}
  .keywords span {{
    display: inline-block;
    background: #f1eefc;
    color: #4b3aa4;
    font-size: 0.78rem;
    padding: 0.12rem 0.55rem;
    border-radius: 6px;
    margin: 0.2rem 0.3rem 0 0;
  }}
  a {{ color: #6a4fc2; }}
  .listen-link {{ font-size: 0.85rem; font-weight: 600; }}
  footer {{ margin-top: 2.5rem; font-size: 0.8rem; color: #888; line-height: 1.6; }}
  footer p {{ margin: 0 0 0.6rem; }}
  .empty {{ color: #666; font-style: italic; }}
  @media (prefers-color-scheme: dark) {{
    body {{ background: #121212; color: #eaeaea; }}
    .card {{ background: #1c1c1e; border-color: #2e2e2e; }}
    .card h2 {{ color: #fff; }}
    .podcast-name {{ color: #999; }}
    .meta {{ color: #bbb; }}
    .meta strong {{ color: #f2f2f2; }}
    .keywords span {{ background: #2a2440; color: #c9bdf5; }}
    .avatar {{ background: #2a2440; color: #c9bdf5; }}
    nav.site-nav a {{ border-color: #3a3a3a; color: #ccc; }}
    nav.site-nav a.active {{ background: #eaeaea; color: #121212; border-color: #eaeaea; }}
    footer {{ color: #888; }}
  }}
</style>
</head>
<body>
<header>
  <p class="eyebrow">{eyebrow}</p>
  <h1>{page_h1}</h1>
  <p class="subtitle">{page_subtitle}</p>
  <p class="meta-line">Last updated: {generated_at} &middot; {count} flagged episode(s)</p>
  {nav}
</header>
{body}
<footer>
  {note}
  <p>Generated by the <a href="https://github.com/elipstein/Eli_Podcast_Monitor">Eli_Podcast_Monitor</a> scan.</p>
</footer>
</body>
</html>
"""

_CARD_TEMPLATE = """<div class="card conf-{conf_class}">
  <div class="card-head">
    <div class="avatar">{initial}</div>
    <div>
      <h2 dir="auto">{title}</h2>
      <div class="podcast-name" dir="auto">{podcast}</div>
    </div>
  </div>
  <p class="meta"><strong>Release date:</strong> {date} &middot; <strong>Confidence:</strong> <span class="badge {conf_class}">{confidence}</span></p>
  <p class="meta" dir="auto"><strong>Reason:</strong> {reason}</p>
  {keywords_block}
  {link}
</div>
"""


def to_html(
    flagged: list[FlaggedEpisode],
    generated_at: datetime | None = None,
    note: str = "",
    page_title: str = "Eli Podcast Monitor",
    eyebrow: str = "Podcast monitor",
    page_h1: str = "Eli Podcast Monitor",
    page_subtitle: str = "Middle Eastern / Israeli cuisine &amp; behind-the-scenes chef content, flagged from monitored podcasts.",
    nav: str = "",
) -> str:
    generated_at = generated_at or datetime.now(timezone.utc)
    generated_str = generated_at.strftime("%Y-%m-%d %H:%M UTC")
    note_html = f"<p>{escape(note)}</p>" if note else ""
    common = dict(
        generated_at=generated_str,
        note=note_html,
        page_title=escape(page_title),
        eyebrow=escape(eyebrow),
        page_h1=escape(page_h1),
        page_subtitle=page_subtitle,
        nav=nav,
    )

    if not flagged:
        body = '<p class="empty">No episodes matched the criteria in the most recent scan.</p>'
        return _HTML_TEMPLATE.format(body=body, count=0, **common)

    cards = []
    for f in sorted(flagged, key=lambda x: x.episode.published or datetime.min.replace(tzinfo=timezone.utc), reverse=True):
        ep, res = f.episode, f.result
        conf_class = _CONFIDENCE_CLASS.get(res.confidence, "low")
        keywords = sorted({m.text for m in res.matched_keywords})
        keywords_block = (
            '<p class="meta keywords" dir="auto"><strong>Matched keywords:</strong><br>'
            + "".join(f"<span>{escape(k)}</span>" for k in keywords)
            + "</p>"
            if keywords
            else ""
        )
        link_html = (
            f'<p class="meta listen-link"><a href="{escape(ep.link)}">Listen / show notes &rarr;</a></p>'
            if ep.link
            else ""
        )
        initial = (ep.podcast_name.strip()[:1] or "?").upper()
        cards.append(
            _CARD_TEMPLATE.format(
                title=escape(ep.title),
                podcast=escape(ep.podcast_name),
                date=_fmt_date(ep.published),
                conf_class=conf_class,
                confidence=escape(res.confidence),
                reason=escape(res.reason),
                keywords_block=keywords_block,
                link=link_html,
                initial=escape(initial),
            )
        )
    return _HTML_TEMPLATE.format(body="\n".join(cards), count=len(flagged), **common)


def to_dicts(flagged: list[FlaggedEpisode]) -> list[dict]:
    out = []
    for f in flagged:
        ep, res = f.episode, f.result
        out.append(
            {
                "podcast_name": ep.podcast_name,
                "episode_title": ep.title,
                "release_date": _fmt_date(ep.published),
                "matched_keywords": sorted({m.text for m in res.matched_keywords}),
                "reason_for_flag": res.reason,
                "confidence": res.confidence,
                "link": ep.link,
            }
        )
    return out
