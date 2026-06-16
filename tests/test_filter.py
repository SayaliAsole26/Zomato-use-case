"""Tests for candidate filter."""

import pytest

from src.config.settings import Settings
from src.integration.filter import filter_candidates
from src.models.preferences import Budget, UserPreferences
from src.models.restaurant import CostTier, RestaurantRecord


@pytest.fixture
def sample_records():
    """Create sample restaurant records for testing."""
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
        RestaurantRecord(
            id="3",
            name="Budget Bites",
            location="Bangalore",
            cuisines=["north indian", "street food"],
            rating=3.8,
            cost_for_two=300,
            cost_tier=CostTier.LOW,
            address="789 Pine Rd",
            votes=200,
        ),
        RestaurantRecord(
            id="4",
            name="Fine Dining",
            location="Mumbai",
            cuisines=["continental", "fine dining"],
            rating=4.8,
            cost_for_two=2000,
            cost_tier=CostTier.HIGH,
            address="100 Marine Dr",
            votes=300,
        ),
        RestaurantRecord(
            id="5",
            name="Cafe Corner",
            location="Bangalore",
            cuisines=["cafe", "italian"],
            rating=4.0,
            cost_for_two=400,
            cost_tier=CostTier.LOW,
            address="200 MG Road",
            votes=50,
        ),
        RestaurantRecord(
            id="6",
            name="No Rating Place",
            location="Bangalore",
            cuisines=["biryani"],
            rating=None,
            cost_for_two=500,
            cost_tier=CostTier.LOW,
            address="300 Brigade Rd",
            votes=10,
        ),
    ]


def test_location_filter(sample_records, test_settings):
    """Test location filtering (case-insensitive)."""
    prefs = UserPreferences(location="bangalore", budget=Budget.LOW)
    result = filter_candidates(sample_records, prefs, settings=test_settings)
    
    # Should only include Bangalore restaurants
    assert all(r.location.lower() == "bangalore" for r in result)
    assert len(result) == 3  # Bangalore LOW records


def test_location_filter_exact_match(sample_records, test_settings):
    """Test location filtering with exact case."""
    prefs = UserPreferences(location="Mumbai", budget=Budget.HIGH)
    result = filter_candidates(sample_records, prefs, settings=test_settings)
    
    assert len(result) == 1
    assert result[0].location == "Mumbai"


def test_budget_filter(sample_records, test_settings):
    """Test budget tier filtering."""
    prefs = UserPreferences(location="Bangalore", budget=Budget.MEDIUM)
    result = filter_candidates(sample_records, prefs, settings=test_settings)
    
    # Should only include MEDIUM tier restaurants
    assert all(r.cost_tier == CostTier.MEDIUM for r in result)
    assert len(result) == 2  # Italian Place and Chinese Wok


def test_budget_filter_low(sample_records, test_settings):
    """Test low budget tier filtering."""
    prefs = UserPreferences(location="Bangalore", budget=Budget.LOW)
    result = filter_candidates(sample_records, prefs, settings=test_settings)
    
    assert all(r.cost_tier == CostTier.LOW for r in result)
    assert len(result) == 3  # Budget Bites, Cafe Corner, No Rating Place


def test_cuisine_filter(sample_records, test_settings):
    """Test cuisine filtering (substring match)."""
    prefs = UserPreferences(
        location="Bangalore",
        budget=Budget.LOW,
        cuisine="italian"
    )
    result = filter_candidates(sample_records, prefs, settings=test_settings)
    
    # Should include restaurants with "italian" in cuisines
    assert len(result) == 1
    assert result[0].name == "Cafe Corner"


def test_cuisine_filter_case_insensitive(sample_records, test_settings):
    """Test cuisine filtering is case-insensitive."""
    prefs = UserPreferences(
        location="Bangalore",
        budget=Budget.LOW,
        cuisine="ITALIAN"
    )
    result = filter_candidates(sample_records, prefs, settings=test_settings)
    
    assert len(result) == 1
    assert result[0].name == "Cafe Corner"


def test_cuisine_filter_optional(sample_records, test_settings):
    """Test cuisine filter is optional (None means no filter)."""
    prefs = UserPreferences(location="Bangalore", budget=Budget.LOW, cuisine=None)
    result = filter_candidates(sample_records, prefs, settings=test_settings)
    
    # Should return all LOW tier Bangalore restaurants
    assert len(result) == 3


def test_rating_filter(sample_records, test_settings):
    """Test minimum rating filtering."""
    prefs = UserPreferences(
        location="Bangalore",
        budget=Budget.LOW,
        min_rating=4.0
    )
    result = filter_candidates(sample_records, prefs, settings=test_settings)
    
    # Should only include restaurants with rating >= 4.0
    assert all(r.rating is not None and r.rating >= 4.0 for r in result)
    assert len(result) == 1  # Only Cafe Corner has rating >= 4.0 among LOW tier


def test_rating_filter_optional(sample_records, test_settings):
    """Test rating filter is optional (None means no filter)."""
    prefs = UserPreferences(location="Bangalore", budget=Budget.LOW, min_rating=None)
    result = filter_candidates(sample_records, prefs, settings=test_settings)
    
    # Should include restaurants with None rating
    assert len(result) == 3


def test_combined_filters(sample_records, test_settings):
    """Test combined location, budget, cuisine, and rating filters."""
    prefs = UserPreferences(
        location="Bangalore",
        budget=Budget.MEDIUM,
        cuisine="italian",
        min_rating=4.0
    )
    result = filter_candidates(sample_records, prefs, settings=test_settings)
    
    # Italian Place: Bangalore, MEDIUM, italian, 4.5 rating
    assert len(result) == 1
    assert result[0].name == "Italian Place"


def test_sort_by_rating_desc(sample_records, test_settings):
    """Test sorting by rating (descending)."""
    prefs = UserPreferences(location="Bangalore", budget=Budget.MEDIUM)
    result = filter_candidates(sample_records, prefs, settings=test_settings)
    
    # Should be sorted by rating desc: 4.5, 4.2
    assert result[0].rating == 4.5
    assert result[1].rating == 4.2


def test_sort_by_votes_tiebreaker(sample_records, test_settings):
    """Test votes as tiebreaker when ratings are equal."""
    # Create records with same rating but different votes
    records = [
        RestaurantRecord(
            id="1",
            name="Place A",
            location="Bangalore",
            cuisines=["test"],
            rating=4.0,
            cost_for_two=500,
            cost_tier=CostTier.LOW,
            address="A",
            votes=50,
        ),
        RestaurantRecord(
            id="2",
            name="Place B",
            location="Bangalore",
            cuisines=["test"],
            rating=4.0,
            cost_for_two=500,
            cost_tier=CostTier.LOW,
            address="B",
            votes=100,
        ),
    ]
    
    prefs = UserPreferences(location="Bangalore", budget=Budget.LOW)
    result = filter_candidates(records, prefs, settings=test_settings)
    
    # Place B should come first (higher votes)
    assert result[0].name == "Place B"
    assert result[1].name == "Place A"


def test_missing_rating_sorted_last(sample_records, test_settings):
    """Test records with missing rating are sorted last."""
    prefs = UserPreferences(location="Bangalore", budget=Budget.LOW)
    result = filter_candidates(sample_records, prefs, settings=test_settings)
    
    # No Rating Place should be last
    assert result[-1].name == "No Rating Place"
    assert result[-1].rating is None


def test_cap_candidates(sample_records, test_settings):
    """Test capping candidates to MAX_CANDIDATES_FOR_LLM."""
    # Create more records than the cap
    records = []
    for i in range(50):
        records.append(
            RestaurantRecord(
                id=str(i),
                name=f"Place {i}",
                location="Bangalore",
                cuisines=["test"],
                rating=4.0,
                cost_for_two=500,
                cost_tier=CostTier.LOW,
                address=str(i),
                votes=i,
            )
        )
    
    prefs = UserPreferences(location="Bangalore", budget=Budget.LOW)
    result = filter_candidates(records, prefs, settings=test_settings)
    
    # Should be capped to max_candidates_for_llm (default 30 in test_settings)
    assert len(result) == test_settings.max_candidates_for_llm


def test_empty_result_no_matches(sample_records, test_settings):
    """Test empty result when no records match filters."""
    prefs = UserPreferences(
        location="Chennai",  # Not in sample
        budget=Budget.LOW
    )
    result = filter_candidates(sample_records, prefs, settings=test_settings)
    
    assert result == []


def test_empty_result_budget_mismatch(sample_records, test_settings):
    """Test empty result when budget tier has no matches."""
    prefs = UserPreferences(location="Bangalore", budget=Budget.HIGH)
    result = filter_candidates(sample_records, prefs, settings=test_settings)
    
    assert result == []


def test_integration_scenario_bangalore_medium_italian(sample_records, test_settings):
    """Test acceptance criteria scenario: Bangalore + medium + Italian + min 4.0."""
    prefs = UserPreferences(
        location="Bangalore",
        budget=Budget.MEDIUM,
        cuisine="Italian",
        min_rating=4.0
    )
    result = filter_candidates(sample_records, prefs, settings=test_settings)
    
    # Should return only Italian Place
    assert len(result) == 1
    assert result[0].name == "Italian Place"
    assert result[0].location == "Bangalore"
    assert result[0].cost_tier == CostTier.MEDIUM
    assert "italian" in result[0].cuisines
    assert result[0].rating >= 4.0


def test_filter_logs_input_and_output_counts(sample_records, test_settings, caplog):
    """Test that filter logs input_count and output_count."""
    import logging

    prefs = UserPreferences(location="Bangalore", budget=Budget.MEDIUM)
    with caplog.at_level(logging.INFO, logger="src.integration.filter"):
        filter_candidates(sample_records, prefs, settings=test_settings)

    assert "filter.input_count=6" in caplog.text
    assert "filter.output_count=2" in caplog.text
