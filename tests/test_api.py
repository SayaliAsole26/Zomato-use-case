"""Tests for FastAPI REST API (Phase 8.6)."""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.deps import get_llm_client_dep, get_repository_dep
from src.api.main import FRONTEND_DIST, _to_api_response, create_app
from src.models.recommendation import EmptyResult, RecommendationItem, RecommendationMeta, RecommendationResponse
from src.models.restaurant import CostTier, RestaurantRecord


@pytest.fixture
def sample_candidates():
    return [
        RestaurantRecord(
            id="1",
            name="Italian Place",
            location="BTM",
            cuisines=["italian", "north indian"],
            rating=4.5,
            cost_for_two=800,
            cost_tier=CostTier.MEDIUM,
            address="123 Main St",
            votes=120,
        ),
    ]


@pytest.fixture
def mock_repository(sample_candidates):
    mock_repo = Mock()
    mock_repo.query.return_value = sample_candidates
    mock_repo.get_locations.return_value = ["BTM", "Banashankari"]
    mock_repo.count.return_value = len(sample_candidates)
    return mock_repo


@pytest.fixture
def mock_llm_client():
    mock_client = Mock()
    mock_client.complete.return_value = """{
  "summary": "Top picks in BTM",
  "recommendations": [
    {"restaurant_id": "1", "rank": 1, "explanation": "Excellent Italian cuisine"}
  ]
}"""
    return mock_client


@pytest.fixture
def api_client(mock_repository, mock_llm_client):
    app = create_app(enable_rate_limit=False, mount_frontend=False, preload_dataset=False)
    app.dependency_overrides[get_repository_dep] = lambda: mock_repository
    app.dependency_overrides[get_llm_client_dep] = lambda: mock_llm_client

    with TestClient(app) as test_client:
        test_client.app.state.dataset_ready = True
        test_client.app.state.restaurant_count = mock_repository.count.return_value
        yield test_client

    app.dependency_overrides.clear()


def test_health_returns_dataset_status(api_client, mock_repository):
    response = api_client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["dataset_loaded"] is True
    assert body["restaurant_count"] == mock_repository.count.return_value


def test_root_returns_json_without_frontend_dist(api_client):
    response = api_client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "CulinaAI Restaurant Recommendations API"
    assert body["health"] == "/health"
    assert body["docs"] == "/docs"


def test_recommendations_success(api_client, mock_llm_client):
    payload = {
        "location": "BTM",
        "budget": "medium",
        "cuisine": "North Indian",
        "min_rating": 4.0,
        "additional": ["family-friendly"],
        "max_results": 5,
    }

    response = api_client.post("/api/v1/recommendations", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == "Top picks in BTM"
    assert len(body["recommendations"]) == 1
    assert body["recommendations"][0]["name"] == "Italian Place"
    assert body["recommendations"][0]["rank"] == 1
    assert body["meta"]["candidates_considered"] == 1
    assert body["message"] is None
    mock_llm_client.complete.assert_called_once()


def test_recommendations_validation_error(api_client):
    response = api_client.post(
        "/api/v1/recommendations",
        json={"location": "", "budget": "medium"},
    )

    assert response.status_code == 422


def test_recommendations_empty_filters_return_200(api_client, mock_repository, mock_llm_client):
    mock_repository.query.return_value = []

    response = api_client.post(
        "/api/v1/recommendations",
        json={"location": "BTM", "budget": "low"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["recommendations"] == []
    assert body["message"] is not None
    assert body["suggestions"]
    assert body["meta"]["candidates_considered"] == 0
    mock_llm_client.complete.assert_not_called()


def test_recommendations_invalid_preferences_returns_422(api_client):
    with patch("src.api.main.recommend", side_effect=ValueError("Invalid preferences: bad location")):
        response = api_client.post(
            "/api/v1/recommendations",
            json={"location": "BTM", "budget": "medium"},
        )

    assert response.status_code == 422
    assert "Invalid preferences" in response.json()["detail"]


def test_locations_endpoint(api_client, mock_repository):
    mock_repository.get_locations.return_value = ["BTM", "Banashankari"]
    response = api_client.get("/api/v1/locations")

    assert response.status_code == 200
    body = response.json()
    assert body["locations"] == ["BTM", "Banashankari"]


def test_serve_frontend_when_mounted(mock_repository, mock_llm_client):
    if not FRONTEND_DIST.is_dir():
        import pytest

        pytest.skip("frontend/dist not built — run npm run build in frontend/")

    app = create_app(enable_rate_limit=False, mount_frontend=True)
    app.dependency_overrides[get_repository_dep] = lambda: mock_repository

    with TestClient(app) as client:
        home = client.get("/")
        assert home.status_code == 200
        assert "CulinaAI" in home.text
        discover = client.get("/discover")
        assert discover.status_code == 200

    app.dependency_overrides.clear()


def test_openapi_docs_available(api_client):
    response = api_client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "CulinaAI Restaurant Recommendations"
    assert "/api/v1/recommendations" in schema["paths"]


def test_to_api_response_from_orchestrator_types():
    empty = _to_api_response(EmptyResult())
    assert empty.recommendations == []
    assert empty.message is not None

    success = _to_api_response(
        RecommendationResponse(
            summary="Test",
            recommendations=[
                RecommendationItem(
                    restaurant_id="1",
                    name="Test",
                    cuisine="Italian",
                    rating=4.0,
                    estimated_cost="₹800",
                    explanation="Good",
                    rank=1,
                )
            ],
            meta=RecommendationMeta(candidates_considered=3, latency_ms=100),
        )
    )
    assert len(success.recommendations) == 1
    assert success.meta.candidates_considered == 3
