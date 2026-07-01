"""Keyword and flagging-rule definitions for the podcast monitor.

Most entries here come from the original project brief; the chef list
has since grown with Eli's personal favorites (see LASHEVET_LAKACHAT_GUESTS
and OTHER_FAVORITE_CHEFS below). Keep the four categories (chefs, cuisine
terms, ingredients/dishes, signals) and the five combination rules in
sync with any future keyword additions.

Hebrew support: Eli listens to Hebrew-language shows too, so every
concept below is stored as a list of surface forms in whatever
languages are relevant (English + Hebrew) rather than a single string.
See `_contains` in matcher.py for how Hebrew tokens are matched
differently from English ones (no word-boundary requirement, since
Hebrew attaches prefixes like ה/ב/ל/מ directly with no space).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Category(str, Enum):
    CHEF = "chef"
    CUISINE = "cuisine"
    INGREDIENT = "ingredient"
    SIGNAL = "signal"


def _flatten(*groups: list[str]) -> list[str]:
    return [term for group in groups for term in group]


# Chef names associated with Israeli / Levantine / Mizrahi cuisine, from
# the original brief.
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

# Guests of the Hebrew restaurant-industry podcast "לשבת לקחת" (Lashevet
# Lakachat) -- Eli said any of its past guests is a chef he likes, so a
# chef-interview episode about any of them on *any* podcast should flag.
# This list was hand-seeded from web search results (episodes 1-51) and
# is not exhaustive -- add names as new episodes/guests turn up.
LASHEVET_LAKACHAT_GUESTS = [
    "אורן אסידו",       # Oren Assido
    "אייל שני",          # Eyal Shani
    "שחר סגל",           # Shahar Segal
    "נאיפה מולא",        # Na'ifa Mula
    "מושיק רוט",         # Moshik Roth
    "ישראל אהרוני",      # Israel Aharoni
    "תומר אגאי",         # Tomer Agay
    "שחף שבתאי",         # Shahaf Shabtai
    "שגב משה",           # Sagev Moshe
    "יורם ירזין",        # Yoram Yerzin
    "ארי ירזין",         # Ari Yerzin
    "סטיבן לובל",        # Steven Lobel
    "חיים כהן",          # Chaim Cohen
    "שלומי סלמון",       # Shlomi Salmon
    "דוד טור",           # David Tur
    "רן שמואלי",         # Ran Shmueli
    "אבי ביטון",         # Avi Biton
]

# Other chefs/restaurateurs Eli specifically likes hearing interviews
# with, regardless of region/cuisine -- these fire the same rules as the
# regional chef names (e.g. rule 1: chef-interview signal + this name is
# enough to flag, even with no Levantine/Israeli content in the episode).
# Michael Solomonov is already in CHEF_NAMES above.
OTHER_FAVORITE_CHEFS = [
    "Will Guidara",
    "Danny Meyer",
]

CHEF_NAMES = _flatten(CHEF_NAMES, LASHEVET_LAKACHAT_GUESTS, OTHER_FAVORITE_CHEFS)

# Cuisine / region terms.
CUISINE_TERMS = [
    "Israeli cuisine",
    "Mizrahi",
    "Palestinian food",
    "Levantine",
    "Tel Aviv restaurants",
    "Jerusalem food culture",
    "המטבח הישראלי",       # Israeli cuisine
    "מזרחי",               # Mizrahi
    "אוכל פלסטיני",        # Palestinian food
    "לבנטיני",             # Levantine
    "מסעדות תל אביב",      # Tel Aviv restaurants
    "תרבות האוכל הירושלמית",  # Jerusalem food culture
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
    "חומוס",   # hummus
    "טחינה",   # tahini
    "פיתה",    # pita
    "קובה",    # kubbeh
    "שקשוקה",  # shakshuka
    "זעתר",    # za'atar
    "סומאק",   # sumac
    "לבנה",    # labneh
    "סביח",    # sabich
    "בורקס",   # bourekas
    "מלאווח",  # malawach
    "ג'חנון",  # jachnun
]

# Behind-the-scenes / narrative signal phrases, grouped by concept so the
# combination-rule sets below can reference a whole concept regardless of
# language.
SIGNAL_CONCEPTS: dict[str, list[str]] = {
    "chef_interview": ["chef interview", "ראיון שף", "ראיון עם שף", "ראיון עם השף"],
    "restaurant_kitchen": ["restaurant kitchen", "מטבח המסעדה", "מטבח מסעדה"],
    "menu_development": ["menu development", "פיתוח תפריט"],
    "food_anthropology": ["food anthropology", "אנתרופולוגיה של האוכל", "אנתרופולוגיה קולינרית"],
    "diaspora_cooking": ["diaspora cooking", "בישול הפזורה", "מטבח הגולה"],
    "street_food": ["street food", "אוכל רחוב"],
    "restaurant_opening": ["restaurant opening", "פתיחת מסעדה"],
    "kitchen_culture": ["kitchen culture", "תרבות המטבח"],
}

SIGNAL_TERMS = _flatten(*SIGNAL_CONCEPTS.values())

ALL_KEYWORDS: dict[str, Category] = {
    **{k: Category.CHEF for k in CHEF_NAMES},
    **{k: Category.CUISINE for k in CUISINE_TERMS},
    **{k: Category.INGREDIENT for k in INGREDIENT_TERMS},
    **{k: Category.SIGNAL for k in SIGNAL_TERMS},
}


def _lower(terms):
    return {t.lower() for t in terms}


def _concepts(*names: str) -> set[str]:
    return _lower(_flatten(*[SIGNAL_CONCEPTS[n] for n in names]))


# Signal subsets used by specific combination rules below (all language
# variants of each underlying concept).
CHEF_INTERVIEW_SIGNALS = _concepts("chef_interview")
RESTAURANT_STORY_SIGNALS = _concepts("restaurant_kitchen", "restaurant_opening", "menu_development", "kitchen_culture")
NARRATIVE_SIGNALS = _concepts("food_anthropology", "diaspora_cooking", "street_food")
KITCHEN_TALK_SIGNALS = _concepts("restaurant_kitchen", "kitchen_culture", "menu_development")


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


RULES = [
    Rule(
        id="chef_interview_regional_cuisine",
        description="Chef interview + Middle Eastern / Israeli cuisine",
        left=CHEF_INTERVIEW_SIGNALS,
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
        left=RESTAURANT_STORY_SIGNALS,
        # A named chef, or a cuisine term standing in for "a chef connected
        # to the region" (e.g. "a new Mizrahi restaurant opening").
        right_categories={Category.CHEF, Category.CUISINE},
    ),
    Rule(
        id="cultural_narrative_levant",
        description="Cultural or historical food narrative + Levant region",
        left=NARRATIVE_SIGNALS,
        right_categories={Category.CUISINE},
    ),
    Rule(
        id="kitchen_talk_relevant_keyword",
        description="Behind-the-scenes kitchen talk + relevant chef or dish keyword",
        left=KITCHEN_TALK_SIGNALS,
        right_categories={Category.CHEF, Category.INGREDIENT},
    ),
]
