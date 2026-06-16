"""Tests for prompt builder."""

import pytest

from src.integration.prompt_builder import build_prompt
from src.models.preferences import Budget
from src.models.restaurant import CostTier, RestaurantRecord


@pytest.fixture
def sample_preferences():
    """Create sample user preferences."""
    from src.models.preferences import UserPreferences
    return UserPreferences(
        location="Bangalore",
        budget=Budget.MEDIUM,
        cuisine="Italian",
        min_rating=4.0,
        additional=["family-friendly", "outdoor seating"],
        max_results=5,
    )


@pytest.fixture
def sample_candidates():
    """Create sample restaurant candidates."""
    return [
        RestaurantRecord(
            id="1",
            name="Italian Place",
            location="Bangalore",
            cuisines=["italian", "pizza"],
            rating=4.5,
            cost_for_two=800,
            cost_tier=CostTier.MEDIUM,
            address="123 Main St",
            votes=120,
        ),
        RestaurantRecord(
            id="2",
            name="Chinese Wok",
            location="Bangalore",
            cuisines=["chinese", "asian"],
            rating=4.2,
            cost_for_two=600,
            cost_tier=CostTier.MEDIUM,
            address="456 Oak Ave",
            votes=80,
        ),
    ]


def test_build_prompt_returns_tuple(sample_preferences, sample_candidates):
    """Test that build_prompt returns a tuple of (system, user)."""
    system, user = build_prompt(sample_preferences, sample_candidates)
    
    assert isinstance(system, str)
    assert isinstance(user, str)


def test_system_prompt_contains_constraints(sample_preferences, sample_candidates):
    """Test that system prompt contains important constraints."""
    system, _ = build_prompt(sample_preferences, sample_candidates)
    
    assert "expert restaurant recommendation assistant" in system.lower()
    assert "only recommend restaurants from the provided list" in system.lower()
    assert "json only" in system.lower()
    assert "do not invent" in system.lower()


def test_system_prompt_contains_json_schema(sample_preferences, sample_candidates):
    """Test that system prompt contains JSON schema."""
    system, _ = build_prompt(sample_preferences, sample_candidates)
    
    assert "restaurant_id" in system
    assert "rank" in system
    assert "explanation" in system
    assert "summary" in system


def test_user_prompt_contains_preferences(sample_preferences, sample_candidates):
    """Test that user prompt contains user preferences."""
    _, user = build_prompt(sample_preferences, sample_candidates)
    
    assert "Bangalore" in user
    assert "medium" in user
    assert "Italian" in user
    assert "4.0" in user
    assert "family-friendly" in user
    assert "outdoor seating" in user


def test_user_prompt_contains_candidates(sample_preferences, sample_candidates):
    """Test that user prompt contains candidate information."""
    _, user = build_prompt(sample_preferences, sample_candidates)
    
    assert "Italian Place" in user
    assert "Chinese Wok" in user
    assert "1. ID: 1" in user
    assert "2. ID: 2" in user


def test_user_prompt_with_minimal_preferences(sample_candidates):
    """Test user prompt with minimal preferences."""
    from src.models.preferences import UserPreferences
    prefs = UserPreferences(location="Mumbai", budget=Budget.LOW)
    
    _, user = build_prompt(prefs, sample_candidates)
    
    assert "Mumbai" in user
    assert "low" in user


def test_user_prompt_without_additional_preferences(sample_candidates):
    """Test user prompt without additional preferences."""
    from src.models.preferences import UserPreferences
    prefs = UserPreferences(
        location="Bangalore",
        budget=Budget.MEDIUM,
        cuisine="Italian",
    )
    
    _, user = build_prompt(prefs, sample_candidates)
    
    # Should not contain "Additional preferences" section
    assert "Additional preferences" not in user


def test_user_prompt_respects_max_results(sample_preferences, sample_candidates):
    """Test that max_results is reflected in prompt."""
    system, user = build_prompt(sample_preferences, sample_candidates, max_results=3)
    
    assert "3" in system  # Should mention max results in system prompt
    assert "3" in user  # Should mention max results in user prompt


def test_system_prompt_expert_role(sample_preferences, sample_candidates):
    """Test that system prompt establishes expert role."""
    system, _ = build_prompt(sample_preferences, sample_candidates)
    
    assert "expert" in system.lower()
    assert "rank" in system.lower()


def test_user_prompt_contains_task_instruction(sample_preferences, sample_candidates):
    """Test that user prompt contains clear task instruction."""
    _, user = build_prompt(sample_preferences, sample_candidates)
    
    assert "Task:" in user
    assert "rank" in user.lower()
