"""LLM-based taste matching for Eli's broader listening profile.

Unlike matcher.py's fixed keyword-combination rules (which work for a
narrow, well-defined target like "chef interview + Israeli cuisine"),
there's no keyword set that captures "would Eli like this episode of
Acquired." This module asks Claude to judge episode fit against
PROFILE.md in free text instead.

Requires the `anthropic` package and an ANTHROPIC_API_KEY in the
environment. Untested against the live API from this dev session --
see the "Known limitation" note in README.md.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import anthropic
from pydantic import BaseModel

MODEL = "claude-opus-4-8"

PROFILE_PATH = Path(__file__).resolve().parent.parent / "PROFILE.md"

_SYSTEM_TEMPLATE = """You judge whether a podcast episode is worth recommending \
to Eli, based on his listening profile below. Be selective: most episodes of a \
show he already likes are still not worth a special recommendation. Flag an \
episode only if it's unusually good, timely, or distinctive relative to that \
show's normal output, or if it features a person Eli has specifically said he \
likes hearing from.

{profile}
"""


class EpisodeJudgment(BaseModel):
    fits: bool
    confidence: Literal["High", "Medium", "Low"]
    reasoning: str


def load_profile(path: Path = PROFILE_PATH) -> str:
    return path.read_text()


def judge_episode(
    client: anthropic.Anthropic,
    profile_text: str,
    podcast_name: str,
    title: str,
    description: str,
) -> EpisodeJudgment:
    """Ask Claude whether this specific episode fits Eli's taste profile."""
    response = client.messages.parse(
        model=MODEL,
        max_tokens=1024,
        system=_SYSTEM_TEMPLATE.format(profile=profile_text),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Podcast: {podcast_name}\n"
                    f"Episode title: {title}\n"
                    f"Description: {description}\n\n"
                    "Does this specific episode fit Eli's taste profile well "
                    "enough to recommend?"
                ),
            }
        ],
        output_format=EpisodeJudgment,
    )
    return response.parsed_output
