"""Tests for UserPreferences model and validation."""

import pytest

from src.models.preferences import Budget, UserPreferences, resolve_max_results, validate_preferences
from pydantic import ValidationError


def test_valid_preferences():
    """Test creating valid UserPreferences."""
    prefs = UserPreferences(
        location="Bangalore",
        budget=Budget.MEDIUM,
        cuisine="Italian",
        min_rating=4.0,
        additional=["family-friendly", "outdoor seating"],
        max_results=5,
    )
    assert prefs.location == "Bangalore"
    assert prefs.budget == Budget.MEDIUM
    assert prefs.cuisine == "Italian"
    assert prefs.min_rating == 4.0
    assert prefs.additional == ["family-friendly", "outdoor seating"]
    assert prefs.max_results == 5


def test_minimal_preferences():
    """Test creating UserPreferences with only required fields."""
    prefs = UserPreferences(location="Mumbai", budget=Budget.LOW)
    assert prefs.location == "Mumbai"
    assert prefs.budget == Budget.LOW
    assert prefs.cuisine is None
    assert prefs.min_rating is None
    assert prefs.additional == []
    assert prefs.max_results is None


def test_empty_location_raises_error():
    """Test that empty location raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        UserPreferences(location="", budget=Budget.MEDIUM)
    assert "location cannot be empty" in str(exc_info.value).lower()


def test_whitespace_only_location_raises_error():
    """Test that whitespace-only location raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        UserPreferences(location="   ", budget=Budget.MEDIUM)
    assert "location cannot be empty" in str(exc_info.value).lower()


def test_invalid_budget_raises_error():
    """Test that invalid budget string raises validation error."""
    with pytest.raises(ValidationError):
        UserPreferences(location="Bangalore", budget="premium")


def test_rating_out_of_range_raises_error():
    """Test that rating outside 0-5 range raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        UserPreferences(location="Bangalore", budget=Budget.MEDIUM, min_rating=6.0)
    assert "rating must be between 0 and 5" in str(exc_info.value).lower()


def test_negative_rating_raises_error():
    """Test that negative rating raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        UserPreferences(location="Bangalore", budget=Budget.MEDIUM, min_rating=-1.0)
    assert "rating must be between 0 and 5" in str(exc_info.value).lower()


def test_rating_none_is_valid():
    """Test that None rating is valid (optional field)."""
    prefs = UserPreferences(location="Bangalore", budget=Budget.MEDIUM, min_rating=None)
    assert prefs.min_rating is None


def test_max_results_out_of_range_raises_error():
    """Test that max_results outside 1-20 range raises validation error."""
    with pytest.raises(ValidationError):
        UserPreferences(location="Bangalore", budget=Budget.MEDIUM, max_results=0)
    
    with pytest.raises(ValidationError):
        UserPreferences(location="Bangalore", budget=Budget.MEDIUM, max_results=25)


def test_location_trimming():
    """Test that location is trimmed of whitespace."""
    prefs = UserPreferences(location="  Bangalore  ", budget=Budget.MEDIUM)
    assert prefs.location == "Bangalore"


def test_validate_preferences_with_known_location():
    """Test validation with location in known locations list."""
    prefs = UserPreferences(location="Bangalore", budget=Budget.MEDIUM)
    known_locations = ["Bangalore", "Mumbai", "New Delhi"]
    
    is_valid, warnings = validate_preferences(prefs, known_locations)
    assert is_valid is True
    assert len(warnings) == 0


def test_validate_preferences_with_unknown_location():
    """Test validation with location not in known locations list."""
    prefs = UserPreferences(location="Chennai", budget=Budget.MEDIUM)
    known_locations = ["Bangalore", "Mumbai", "New Delhi"]
    
    is_valid, warnings = validate_preferences(prefs, known_locations)
    assert is_valid is True
    assert len(warnings) == 1
    assert "not found in known locations" in warnings[0].lower()


def test_validate_preferences_case_insensitive():
    """Test that location matching is case-insensitive."""
    prefs = UserPreferences(location="bangalore", budget=Budget.MEDIUM)
    known_locations = ["Bangalore", "Mumbai", "New Delhi"]
    
    is_valid, warnings = validate_preferences(prefs, known_locations)
    assert is_valid is True
    assert len(warnings) == 0


def test_validate_preferences_without_known_locations():
    """Test validation without providing known locations list."""
    prefs = UserPreferences(location="Bangalore", budget=Budget.MEDIUM)
    
    is_valid, warnings = validate_preferences(prefs, None)
    assert is_valid is True
    assert len(warnings) == 0


def test_budget_enum_values():
    """Test that Budget enum has expected values."""
    assert Budget.LOW.value == "low"
    assert Budget.MEDIUM.value == "medium"
    assert Budget.HIGH.value == "high"


def test_cuisine_whitespace_treated_as_none():
    """Whitespace-only cuisine is treated as omitted."""
    prefs = UserPreferences(location="Bangalore", budget=Budget.MEDIUM, cuisine="   ")
    assert prefs.cuisine is None


def test_additional_tags_trimmed():
    """Additional tags are trimmed and empty entries removed."""
    prefs = UserPreferences(
        location="Bangalore",
        budget=Budget.MEDIUM,
        additional=[" family-friendly ", "", "  quick service  "],
    )
    assert prefs.additional == ["family-friendly", "quick service"]


def test_resolve_max_results_uses_preference_when_set(test_settings):
    prefs = UserPreferences(location="Bangalore", budget=Budget.MEDIUM, max_results=3)
    assert resolve_max_results(prefs, settings=test_settings) == 3


def test_resolve_max_results_defaults_to_settings(test_settings):
    prefs = UserPreferences(location="Bangalore", budget=Budget.MEDIUM)
    assert resolve_max_results(prefs, settings=test_settings) == test_settings.max_results
