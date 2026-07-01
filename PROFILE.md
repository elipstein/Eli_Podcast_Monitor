# Eli's Listening Profile

This tracks what Eli actually listens to, why, and what that implies
for recommending new podcasts and episodes. It's broader than the
Middle Eastern/Israeli cuisine matcher (`podcast_monitor/`) — that
tool flags specific *episodes* against a fixed rule set; this file is
the human-readable taste model behind *recommendations*, updated as
Eli tells me more about what he listens to.

## Subscriptions, by theme

**Israeli / Jewish food & restaurant culture** (the original project focus)
- לשבת לקחת — chef/restaurateur interviews (guest list tracked in `keywords.py`)
- מדברים מהבטן — Israeli restaurant & food-culture trends
- מאחורי הצלחת עם גדי חן — chef/restaurateur interviews (guest list tracked)

**Hospitality & restaurant-industry business storytelling**
- (via chef-interview flagging) Will Guidara, Danny Meyer — hospitality philosophy, leadership, why restaurants succeed/fail

**Long-form intellectual / scientific conversation**
- Sam Harris (Making Sense) — philosophy, rationality, long-form interviews
- Rhonda Patrick (FoundMyFitness) — nutrition, longevity, science deep dives

**Unfiltered / observational comedy & conversation**
- Bill Maher (Club Random / Real Time) — political comedy, freewheeling guest conversation
- Absolutely Mental with Ricky Gervais — "LOVE LOVE"s this one

**Business & tech commentary**
- Pivot (Kara Swisher & Scott Galloway) — tech/business news with opinionated banter

**Narrative / storytelling**
- The Moth — true stories, told live, no notes
- Israel Story — true stories about ordinary Israelis (also a food-culture crossover)

**Israeli news & current affairs**
- השבוע — פודקאסט הארץ (Haaretz) — weekly Hebrew news roundup

**Jewish culture, comedy & philosophy**
- And Here's Modi — Jewish comedian Modi Rosenfeld, unfiltered, comedy + spirituality
- Think & Drink Different — Jeremy Fogel ("is so great!!!"), Jewish philosophy/theology; Fogel also co-hosts a כאן culinary-history documentary with chef Asaf Doktor, which is why both are now tracked in `OTHER_FAVORITE_CHEFS`

**Niche hobbyist**
- The Daily Churn — travel hacking / points & miles / FIRE

## What this suggests about taste

- Long, unstructured, personality-driven conversation over tightly
  produced segments (Sam Harris, Bill Maher's Club Random, Pivot,
  Absolutely Mental all lean this way).
- A consistent pull toward Jewish/Israeli identity and culture across
  very different formats — food (לשבת לקחת), comedy (Modi), news
  (Haaretz), philosophy (Fogel), storytelling (Israel Story).
- Comedy that's willing to be dark, honest, or a little uncomfortable
  (Gervais, Maher, Modi) rather than broad/mainstream.
- Genuine interest in *why things work* in hospitality and business
  specifically, not just food itself (Guidara, Meyer, Pivot, Galloway).

## New podcast recommendations

Not yet added to `podcasts.yaml` (that file is for the food/chef
matcher specifically) — these are general suggestions based on the
profile above, grouped by which existing subscription they're closest to.

**If you like Sam Harris / Rhonda Patrick** (long-form, science-adjacent)
- *Huberman Lab* (Andrew Huberman) — neuroscience/health, same long-form deep-dive style as Rhonda Patrick
- *The Tim Ferriss Show* — long-form interviews, performance & decision-making
- *Conversations with Tyler* (Tyler Cowen) — dense, wide-ranging intellectual interviews

**If you like Bill Maher / Ricky Gervais** (unfiltered comedy conversation)
- *WTF with Marc Maron* — raw, personal, long-running comedian interviews
- *Armchair Expert* (Dax Shepard) — candid, occasionally uncomfortable long-form talk
- *SmartLess* (Sean Hayes, Jason Bateman, Will Arnett) — lighter, but same loose comedian-banter format

**If you like Pivot** (business/tech with opinion)
- *The Prof G Pod* (Scott Galloway solo) — same voice as half of Pivot, more solo takes
- *Acquired* — deep-dive business/company histories

**If you like The Moth / Israel Story** (narrative storytelling)
- *This American Life* — the format The Moth borrows from
- *Radiolab* — narrative + science/philosophy hybrid

**If you like Think & Drink Different / And Here's Modi** (Jewish culture, philosophy, comedy)
- *Wondering Jews with Mijal and Noam* — already turned up organically in the food research (a real chef-interview episode with Michael Solomonov) and fits this theme independently: Jewish identity, culture, humor
- *Unorthodox* (Tablet Magazine) — Jewish culture/news roundtable, comparable tone to Modi's "unfiltered" angle
- *Being Jewish with Jonah Platt* — celebrity guests on personal Jewish identity, comedy-adjacent
- *Two Nice Jewish Boys* — Tel Aviv-recorded, casual conversation on Israeli politics/culture/entertainment

**If you like השבוע — פודקאסט הארץ** (Israeli news, but in English too)
- *Haaretz Podcast* (English, hosted by Allison Kaplan Sommer) — same newsroom, English-language weekly
- *Israel Policy Pod* (Israel Policy Forum, hosted by Neri Zilber) — policy-focused analysis beyond headlines

## Open question

Should these general (non-food) recommendations also get pulled into
the automated tooling somehow (e.g. a second `profile_podcasts.yaml`
that gets scanned for *new episodes* worth a look, separate from the
strict Middle-Eastern-cuisine rule engine), or should this file stay a
manually-curated reference that gets refreshed by conversation, like
today? Worth deciding before building more automation here, since the
matching logic that makes sense for "chef interview + Levantine
cuisine" doesn't obviously generalize to "would Eli like this episode
of Acquired."
