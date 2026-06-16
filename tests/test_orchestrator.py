"""Tests for application orchestrator."""

from unittest.mock import Mock, patch

import pytest

from src.models.preferences import Budget, UserPreferences
from src.models.recommendation import EmptyResult, RecommendationResponse
from src.models.restaurant import CostTier, RestaurantRecord
from src.orchestrator import recommend


@pytest.fixture
def sample_preferences():
    return UserPreferences(
        location="Bangalore",
        budget=Budget.MEDIUM,
        cuisine="Italian",
        min_rating=4.0,
        max_results=5,
    )


@pytest.fixture
def sample_candidates():
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


def _mock_repository(candidates: list[RestaurantRecord]) -> Mock:
    mock_repo = Mock()
    mock_repo.query.return_value = candidates
    mock_repo.get_locations.return_value = ["Bangalore", "Mumbai"]
    return mock_repo


def test_recommend_returns_response_with_meta(sample_preferences, sample_candidates):
    with patch("src.orchestrator.get_repository") as mock_repo_getter, patch(
        "src.orchestrator.GroqClient"
    ) as mock_client_class:
        mock_repo_getter.return_value = _mock_repository(sample_candidates)

        mock_client = Mock()
        mock_client.complete.return_value = """{
  "summary": "Top Italian restaurants in Bangalore",
  "recommendations": [
    {
      "restaurant_id": "1",
      "rank": 1,
      "explanation": "Excellent Italian cuisine"
    }
  ]
}"""
        mock_client_class.return_value = mock_client

        result = recommend(sample_preferences)

        assert isinstance(result, RecommendationResponse)
        assert result.meta is not None
        assert result.meta.candidates_considered == len(sample_candidates)
        assert result.meta.latency_ms is not None
        assert result.meta.latency_ms >= 0
        assert result.meta.fallback is False
        mock_client.complete.assert_called_once()


def test_recommend_empty_candidates_returns_empty_result(sample_preferences):
    with patch("src.orchestrator.get_repository") as mock_repo_getter, patch(
        "src.orchestrator.GroqClient"
    ) as mock_client_class:
        mock_repo_getter.return_value = _mock_repository([])

        result = recommend(sample_preferences)

        assert isinstance(result, EmptyResult)
        mock_client_class.assert_not_called()


def test_recommend_uses_fallback_on_llm_failure(sample_preferences, sample_candidates):
    with patch("src.orchestrator.get_repository") as mock_repo_getter, patch(
        "src.orchestrator.GroqClient"
    ) as mock_client_class:
        mock_repo_getter.return_value = _mock_repository(sample_candidates)

        mock_client = Mock()
        mock_client.complete.side_effect = Exception("LLM API error")
        mock_client_class.return_value = mock_client

        result = recommend(sample_preferences)

        assert isinstance(result, RecommendationResponse)
        assert len(result.recommendations) > 0
        assert result.meta is not None
        assert result.meta.fallback is True


def test_recommend_uses_fallback_on_parse_failure(sample_preferences, sample_candidates):
    with patch("src.orchestrator.get_repository") as mock_repo_getter, patch(
        "src.orchestrator.GroqClient"
    ) as mock_client_class:
        mock_repo_getter.return_value = _mock_repository(sample_candidates)

        mock_client = Mock()
        mock_client.complete.return_value = "This is not valid JSON"
        mock_client_class.return_value = mock_client

        result = recommend(sample_preferences)

        assert isinstance(result, RecommendationResponse)
        assert len(result.recommendations) > 0
        assert result.meta is not None
        assert result.meta.fallback is True


def test_recommend_validates_preferences():
    with patch("src.orchestrator.get_repository") as mock_repo_getter, patch(
        "src.orchestrator.validate_preferences"
    ) as mock_validate:
        mock_repo_getter.return_value = _mock_repository([])
        mock_validate.return_value = (False, ["Invalid location"])

        prefs = UserPreferences(location="Bangalore", budget=Budget.MEDIUM)

        with pytest.raises(ValueError, match="Invalid preferences"):
            recommend(prefs)


def test_recommend_with_validation_warnings(sample_preferences, sample_candidates):
    with patch("src.orchestrator.get_repository") as mock_repo_getter, patch(
        "src.orchestrator.validate_preferences"
    ) as mock_validate, patch("src.orchestrator.GroqClient") as mock_client_class:
        mock_validate.return_value = (True, ["Location not in known list"])
        mock_repo_getter.return_value = _mock_repository(sample_candidates)

        mock_client = Mock()
        mock_client.complete.return_value = """{
  "recommendations": [
    {"restaurant_id": "1", "rank": 1, "explanation": "Good choice"}
  ]
}"""
        mock_client_class.return_value = mock_client

        result = recommend(sample_preferences)
        assert isinstance(result, RecommendationResponse)


def test_recommend_respects_max_results(sample_candidates):
    with patch("src.orchestrator.get_repository") as mock_repo_getter, patch(
        "src.orchestrator.GroqClient"
    ) as mock_client_class:
        mock_repo_getter.return_value = _mock_repository(sample_candidates)

        mock_client = Mock()
        mock_client.complete.return_value = """{
  "recommendations": [
    {"restaurant_id": "1", "rank": 1, "explanation": "First"},
    {"restaurant_id": "2", "rank": 2, "explanation": "Second"}
  ]
}"""
        mock_client_class.return_value = mock_client

        prefs = UserPreferences(location="Bangalore", budget=Budget.MEDIUM, max_results=1)
        result = recommend(prefs)

        assert len(result.recommendations) <= 1


def test_recommend_accepts_injected_dependencies(sample_preferences, sample_candidates):
    mock_repo = _mock_repository(sample_candidates)
    mock_client = Mock()
    mock_client.complete.return_value = """{
  "recommendations": [
    {"restaurant_id": "1", "rank": 1, "explanation": "Injected client works"}
  ]
}"""

    result = recommend(
        sample_preferences,
        repository=mock_repo,
        llm_client=mock_client,
    )

    assert isinstance(result, RecommendationResponse)
    mock_repo.query.assert_called_once_with(sample_preferences)
    mock_client.complete.assert_called_once()
