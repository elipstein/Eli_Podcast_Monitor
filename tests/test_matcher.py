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
