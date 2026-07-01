"""Keyword and flagging-rule definitions for the podcast monitor.

Every entry here comes straight from the project brief. Keep the four
categories (chefs, cuisine terms, ingredients/dishes, signals) and the
five combination rules in sync with any future keyword additions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Category(str, Enum):
    CHEF = "chef"
    CUISINE = "cuisine"
    INGREDIENT = "ingredient"
    SIGNAL = "signal"


# Chef names associated with Israeli / Levantine / Mizrahi cuisine.
CHEF_NAMES = [
    "Einat Admony",
    "Michael Solomonov",
    "Reem Assil",
    "Avi Shemtov",
    "Ori Menashe",
    "Genevieve Gergis",
    "Erez Komarovsky",
    "Rawia Bishara",
]

# Cuisine / region terms.
CUISINE_TERMS = [
    "Israeli cuisine",
    "Mizrahi",
    "Palestinian food",
    "Levantine",
    "Tel Aviv restaurants",
    "Jerusalem food culture",
]

# Ingredients and dishes.
INGREDIENT_TERMS = [
    "hummus",
    "tahini",
    "pita",
    "kubbeh",
    "shakshuka",
    "za'atar",
    "zaatar",
    "sumac",
    "labneh",
    "sabich",
    "bourekas",
    "malawach",
    "jachnun",
]

# Behind-the-scenes / narrative signal phrases.
SIGNAL_TERMS = [
    "chef interview",
    "restaurant kitchen",
    "menu development",
    "food anthropology",
    "diaspora cooking",
    "street food",
    "restaurant opening",
    "kitchen culture",
]

ALL_KEYWORDS: dict[str, Category] = {
    **{k: Category.CHEF for k in CHEF_NAMES},
    **{k: Category.CUISINE for k in CUISINE_TERMS},
    **{k: Category.INGREDIENT for k in INGREDIENT_TERMS},
    **{k: Category.SIGNAL for k in SIGNAL_TERMS},
}

# Signal subsets used by specific combination rules below.
RESTAURANT_STORY_SIGNALS = {"restaurant kitchen", "restaurant opening", "menu development", "kitchen culture"}
NARRATIVE_SIGNALS = {"food anthropology", "diaspora cooking", "street food"}
KITCHEN_TALK_SIGNALS = {"restaurant kitchen", "kitchen culture", "menu development"}


@dataclass
class Rule:
    """One of the five flagging combination rules from the brief.

    A rule fires when at least one keyword from the "left" side and at
    least one keyword from the "right" side are both present. Each side
    is expressed either as an explicit set of keyword strings, or as
    "any keyword belonging to one of these categories".
    """

    id: str
    description: str
    left: set[str] = field(default_factory=set)
    left_categories: set[Category] = field(default_factory=set)
    right: set[str] = field(default_factory=set)
    right_categories: set[Category] = field(default_factory=set)


def _lower(terms):
    return {t.lower() for t in terms}


RULES = [
    Rule(
        id="chef_interview_regional_cuisine",
        description="Chef interview + Middle Eastern / Israeli cuisine",
        left={"chef interview"},
        # A cuisine term, or one of the named chefs (who are themselves
        # Israeli/Levantine/Mizrahi chefs) standing in for that cuisine.
        right_categories={Category.CUISINE, Category.CHEF},
    ),
    Rule(
        id="ingredient_deep_dive_levantine",
        description="Ingredient deep dive + Levantine origin",
        left_categories={Category.INGREDIENT},
        right_categories={Category.CUISINE},
    ),
    Rule(
        id="restaurant_story_regional_chef",
        description="Restaurant story + Israeli/Mizrahi/Levantine chef",
        left=_lower(RESTAURANT_STORY_SIGNALS),
        # A named chef, or a cuisine term standing in for "a chef connected
        # to the region" (e.g. "a new Mizrahi restaurant opening").
        right_categories={Category.CHEF, Category.CUISINE},
    ),
    Rule(
        id="cultural_narrative_levant",
        description="Cultural or historical food narrative + Levant region",
        left=_lower(NARRATIVE_SIGNALS),
        right_categories={Category.CUISINE},
    ),
    Rule(
        id="kitchen_talk_relevant_keyword",
        description="Behind-the-scenes kitchen talk + relevant chef or dish keyword",
        left=_lower(KITCHEN_TALK_SIGNALS),
        right_categories={Category.CHEF, Category.INGREDIENT},
    ),
]
