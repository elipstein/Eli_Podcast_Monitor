from podcast_monitor.matcher import evaluate


def test_chef_interview_plus_cuisine_flags_high_confidence():
    result = evaluate(
        "Chef Interview: Michael Solomonov on Zahav and Israeli Cuisine",
        "A chef interview about Israeli cuisine, tahini, and hummus.",
    )
    assert result.flagged
    assert "chef_interview_regional_cuisine" in result.fired_rules
    assert result.confidence == "High"


def test_ingredient_deep_dive_with_levantine_origin_flags():
    result = evaluate(
        "The History of Sumac and Za'atar",
        "A deep dive into sumac and za'atar across the Levantine region.",
    )
    assert result.flagged
    assert "ingredient_deep_dive_levantine" in result.fired_rules


def test_restaurant_story_with_named_chef_flags():
    result = evaluate(
        "Reem Assil on Opening Her First Restaurant",
        "A restaurant opening story from chef Reem Assil about building her kitchen culture.",
    )
    assert result.flagged
    assert "restaurant_story_regional_chef" in result.fired_rules


def test_cultural_narrative_with_levant_region_flags():
    result = evaluate(
        "Diaspora Cooking and Food Anthropology",
        "Exploring diaspora cooking and food anthropology within Palestinian food traditions.",
    )
    assert result.flagged
    assert "cultural_narrative_levant" in result.fired_rules


def test_kitchen_talk_with_dish_keyword_flags():
    result = evaluate(
        "Inside the Restaurant Kitchen",
        "Behind-the-scenes restaurant kitchen talk about making shakshuka for brunch service.",
    )
    assert result.flagged
    assert "kitchen_talk_relevant_keyword" in result.fired_rules


def test_chef_interview_with_named_chef_but_no_cuisine_term_flags():
    # The named-chef list exists precisely to identify chef interviews
    # about this region, even when no separate cuisine-term phrase appears.
    result = evaluate(
        "A Chef Interview with Michael Solomonov",
        "A chef interview about his restaurant Zahav and his family history.",
    )
    assert result.flagged
    assert "chef_interview_regional_cuisine" in result.fired_rules


def test_unrelated_episode_not_flagged():
    result = evaluate(
        "Our Favorite Pasta Sauces",
        "A casual chat about weeknight pasta sauces.",
    )
    assert not result.flagged
    assert result.matched_keywords == []


def test_ingredient_mention_alone_without_cuisine_context_not_flagged():
    # "hummus" alone, no chef/cuisine/signal context, shouldn't fire any rule.
    result = evaluate(
        "Weeknight Snacks",
        "We tried a new store-bought hummus brand this week.",
    )
    assert not result.flagged


def test_hebrew_chef_interview_flags():
    result = evaluate(
        "פרק 13: השף ישראל אהרוני",
        "ראיון שף עם ישראל אהרוני על המטבח הישראלי ופתיחת מסעדה חדשה.",
    )
    assert result.flagged
    assert "chef_interview_regional_cuisine" in result.fired_rules
    assert "ישראל אהרוני" in {m.text for m in result.matched_keywords}


def test_hebrew_lashevet_lakachat_guest_flags_on_any_podcast():
    # Eli said: anyone who's ever been a guest on לשבת לקחת counts,
    # even on a totally different show and with no separate cuisine term.
    result = evaluate(
        "ראיון שף עם חיים כהן",
        "שיחה על הקריירה של השף חיים כהן במסעדות כרם ודיקסי.",
    )
    assert result.flagged
    assert "חיים כהן" in {m.text for m in result.matched_keywords}


def test_hebrew_ingredient_with_prefix_still_matches():
    # Hebrew attaches prefixes (ה/ב/ל/מ) with no space, so "החומוס" must
    # still match the "חומוס" (hummus) keyword -- a plain \b-word-boundary
    # match would miss this.
    result = evaluate(
        "הסיפור מאחורי החומוס",
        "אנתרופולוגיה של האוכל: מאיפה הגיע החומוס וטחינה למטבח הלבנטיני.",
    )
    assert result.flagged
    matched = {m.text for m in result.matched_keywords}
    assert "חומוס" in matched
    assert "לבנטיני" in matched


def test_personal_favorite_chef_flags_without_regional_content():
    # Will Guidara / Danny Meyer aren't Levantine chefs, but Eli asked for
    # interviews with them specifically -- a chef-interview signal plus
    # their name should flag on its own, same as the regional chef names.
    result = evaluate(
        "Chef Interview: Will Guidara on Unreasonable Hospitality",
        "A chef interview with restaurateur Will Guidara about his career.",
    )
    assert result.flagged
    assert "chef_interview_regional_cuisine" in result.fired_rules
    assert "Will Guidara" in {m.text for m in result.matched_keywords}

    result2 = evaluate(
        "A Conversation with Danny Meyer",
        "Chef interview with restaurateur Danny Meyer of Union Square Hospitality Group.",
    )
    assert result2.flagged
    assert "Danny Meyer" in {m.text for m in result2.matched_keywords}


def test_hebrew_unrelated_episode_not_flagged():
    result = evaluate(
        "פרק 91: פנינו לאן?",
        "יהונתן ועמית מדברים על תוכניות לחופשה הקרובה, בלי קשר לאוכל מהאזור.",
    )
    assert not result.flagged
