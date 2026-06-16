"""Tests for response parser."""

import pytest

from src.integration.response_parser import (
    _extract_json,
    create_fallback_response,
    parse_response,
)
from src.models.preferences import Budget
from src.models.restaurant import CostTier, RestaurantRecord


@pytest.fixture
def sample_candidates():
    """Create sample restaurant candidates for testing."""
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
    ]


def test_parse_valid_response(sample_candidates):
    """Test parsing a valid LLM response."""
    raw_response = """{
  "summary": "Here are the best Italian restaurants in Bangalore",
  "recommendations": [
    {
      "restaurant_id": "1",
      "rank": 1,
      "explanation": "Excellent Italian cuisine with great ambiance"
    },
    {
      "restaurant_id": "2",
      "rank": 2,
      "explanation": "Good Chinese food at reasonable prices"
    }
  ]
}"""
    
    result = parse_response(raw_response, sample_candidates)
    
    assert result.summary == "Here are the best Italian restaurants in Bangalore"
    assert len(result.recommendations) == 2
    assert result.recommendations[0].restaurant_id == "1"
    assert result.recommendations[0].rank == 1
    assert result.recommendations[0].name == "Italian Place"
    assert result.recommendations[0].cuisine == "italian, pizza"
    assert result.recommendations[0].rating == 4.5
    assert result.recommendations[0].estimated_cost == "₹800 for two"


def test_parse_response_with_markdown(sample_candidates):
    """Test parsing response with markdown code blocks."""
    raw_response = """```json
{
  "summary": "Top recommendations",
  "recommendations": [
    {
      "restaurant_id": "1",
      "rank": 1,
      "explanation": "Great food"
    }
  ]
}
```"""
    
    result = parse_response(raw_response, sample_candidates)
    
    assert len(result.recommendations) == 1
    assert result.recommendations[0].restaurant_id == "1"


def test_parse_response_without_summary(sample_candidates):
    """Test parsing response without optional summary."""
    raw_response = """{
  "recommendations": [
    {
      "restaurant_id": "1",
      "rank": 1,
      "explanation": "Good food"
    }
  ]
}"""
    
    result = parse_response(raw_response, sample_candidates)
    
    assert result.summary is None
    assert len(result.recommendations) == 1


def test_parse_invalid_restaurant_id(sample_candidates):
    """Test that all-invalid restaurant_ids raise error."""
    raw_response = """{
  "recommendations": [
    {
      "restaurant_id": "999",
      "rank": 1,
      "explanation": "Invalid restaurant"
    }
  ]
}"""

    with pytest.raises(ValueError, match="No valid recommendations"):
        parse_response(raw_response, sample_candidates)


def test_parse_missing_explanation_uses_default(sample_candidates):
    """Test that missing explanation gets a generic fallback string."""
    raw_response = """{
  "recommendations": [
    {
      "restaurant_id": "1",
      "rank": 1
    }
  ]
}"""

    result = parse_response(raw_response, sample_candidates)

    assert len(result.recommendations) == 1
    assert "Matches your preferences" in result.recommendations[0].explanation
    """Test that invalid JSON raises error."""
    raw_response = "This is not valid JSON"
    
    with pytest.raises(ValueError, match="Invalid LLM response"):
        parse_response(raw_response, sample_candidates)


def test_parse_sorts_by_rank(sample_candidates):
    """Test that recommendations are sorted by rank."""
    raw_response = """{
  "recommendations": [
    {
      "restaurant_id": "2",
      "rank": 2,
      "explanation": "Second choice"
    },
    {
      "restaurant_id": "1",
      "rank": 1,
      "explanation": "First choice"
    }
  ]
}"""
    
    result = parse_response(raw_response, sample_candidates)
    
    assert result.recommendations[0].rank == 1
    assert result.recommendations[1].rank == 2


def test_parse_caps_to_max_results(sample_candidates):
    """Test that results are capped to max_results."""
    raw_response = """{
  "recommendations": [
    {
      "restaurant_id": "1",
      "rank": 1,
      "explanation": "First"
    },
    {
      "restaurant_id": "2",
      "rank": 2,
      "explanation": "Second"
    },
    {
      "restaurant_id": "3",
      "rank": 3,
      "explanation": "Third"
    }
  ]
}"""
    
    result = parse_response(raw_response, sample_candidates, max_results=2)
    
    assert len(result.recommendations) == 2


def test_extract_json_from_markdown():
    """Test JSON extraction from markdown code blocks."""
    text = """Here's the response:
```json
{"key": "value"}
```
End of response"""
    
    json_str = _extract_json(text)
    assert json_str == '{"key": "value"}'


def test_extract_json_without_markdown():
    """Test JSON extraction without markdown."""
    text = '{"key": "value"}'
    
    json_str = _extract_json(text)
    assert json_str == '{"key": "value"}'


def test_create_fallback_response(sample_candidates):
    """Test fallback response creation."""
    result = create_fallback_response(sample_candidates, max_results=2)
    
    assert len(result.recommendations) == 2
    assert result.summary is None
    
    # Should be sorted by rating (desc)
    assert result.recommendations[0].name == "Italian Place"  # 4.5 rating
    assert result.recommendations[1].name == "Chinese Wok"  # 4.2 rating
    
    # Should have generic explanations
    assert "Highly rated restaurant" in result.recommendations[0].explanation


def test_create_fallback_response_with_missing_rating(sample_candidates):
    """Test fallback with records missing rating."""
    candidates_with_missing = sample_candidates + [
        RestaurantRecord(
            id="4",
            name="No Rating Place",
            location="Bangalore",
            cuisines=["cafe"],
            rating=None,
            cost_for_two=400,
            cost_tier=CostTier.LOW,
            address="X",
            votes=10,
        )
    ]
    
    result = create_fallback_response(candidates_with_missing, max_results=5)
    
    # Records with missing rating should be sorted last
    assert result.recommendations[-1].name == "No Rating Place"


def test_parse_skips_duplicate_restaurant_ids(sample_candidates):
    """Test duplicate restaurant_id entries are deduplicated."""
    raw_response = """{
  "recommendations": [
    {
      "restaurant_id": "1",
      "rank": 1,
      "explanation": "First"
    },
    {
      "restaurant_id": "1",
      "rank": 2,
      "explanation": "Duplicate"
    }
  ]
}"""

    result = parse_response(raw_response, sample_candidates)

    assert len(result.recommendations) == 1
    assert result.recommendations[0].restaurant_id == "1"


def test_parse_skips_invalid_recommendations(sample_candidates):
    """Test that invalid recommendations are skipped."""
    raw_response = """{
  "recommendations": [
    {
      "restaurant_id": "999",
      "rank": 1,
      "explanation": "Invalid"
    },
    {
      "restaurant_id": "1",
      "rank": 2,
      "explanation": "Valid"
    }
  ]
}"""
    
    result = parse_response(raw_response, sample_candidates)
    
    # Should skip the invalid one and keep only valid
    assert len(result.recommendations) == 1
    assert result.recommendations[0].restaurant_id == "1"


def test_parse_empty_recommendations(sample_candidates):
    """Test parsing response with empty recommendations list."""
    raw_response = """{
  "recommendations": []
}"""
    
    result = parse_response(raw_response, sample_candidates)
    
    assert len(result.recommendations) == 0
