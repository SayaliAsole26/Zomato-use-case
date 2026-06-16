"""Tests for Streamlit app helpers (no Streamlit runtime required)."""

from src.app.main import build_preferences_from_form, parse_additional_tags
from src.models.preferences import Budget


def test_parse_additional_tags_empty():
    assert parse_additional_tags("") == []
    assert parse_additional_tags("   ") == []


def test_parse_additional_tags_comma_and_newlines():
    text = "family-friendly, outdoor seating\nquick service"
    assert parse_additional_tags(text) == [
        "family-friendly",
        "outdoor seating",
        "quick service",
    ]


def test_build_preferences_from_form():
    prefs = build_preferences_from_form(
        location="BTM",
        budget_label="Medium",
        cuisine="  North Indian  ",
        min_rating=4.0,
        additional_text="family-friendly",
        max_results=3,
    )
    assert prefs.location == "BTM"
    assert prefs.budget == Budget.MEDIUM
    assert prefs.cuisine == "North Indian"
    assert prefs.min_rating == 4.0
    assert prefs.additional == ["family-friendly"]
    assert prefs.max_results == 3


def test_build_preferences_min_rating_zero_means_none():
    prefs = build_preferences_from_form(
        location="BTM",
        budget_label="Low",
        cuisine="",
        min_rating=0.0,
        additional_text="",
        max_results=5,
    )
    assert prefs.min_rating is None
    assert prefs.cuisine is None
