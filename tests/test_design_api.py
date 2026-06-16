"""Tests for restaurant API routes."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.deps import get_repository_dep
from src.api.main import create_app
from src.models.restaurant import CostTier, RestaurantRecord


class MockRepository:
    def __init__(self, records: list[RestaurantRecord]) -> None:
        self._records = records
        self._by_id = {r.id: r for r in records}

    def get_all(self) -> list[RestaurantRecord]:
        return self._records

    def get_by_id(self, restaurant_id: str) -> RestaurantRecord | None:
        return self._by_id.get(restaurant_id)

    def get_locations(self) -> list[str]:
        return sorted({r.location for r in self._records})

    def count(self) -> int:
        return len(self._records)

    def query(self, prefs) -> list[RestaurantRecord]:
        return self._records


@pytest.fixture
def sample_records():
    return [
        RestaurantRecord(
            id="r1",
            name="Spice Garden",
            location="BTM",
            cuisines=["north indian", "biryani"],
            rating=4.6,
            cost_for_two=600,
            cost_tier=CostTier.MEDIUM,
            votes=500,
        ),
        RestaurantRecord(
            id="r2",
            name="Pizza Hub",
            location="BTM",
            cuisines=["italian", "pizza"],
            rating=4.2,
            cost_for_two=900,
            cost_tier=CostTier.MEDIUM,
            votes=120,
        ),
    ]


@pytest.fixture
def design_client(sample_records):
    mock_repo = MockRepository(sample_records)
    app = create_app(enable_rate_limit=False, mount_frontend=False, preload_dataset=False)
    app.dependency_overrides[get_repository_dep] = lambda: mock_repo

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_restaurant_search_and_detail(design_client):
    search = design_client.get(
        "/api/v1/restaurants/search",
        params={"location": "BTM", "cuisine": "north indian", "min_rating": 4.0},
    )
    assert search.status_code == 200
    body = search.json()
    assert body["total"] >= 1
    assert body["restaurants"][0]["match_score"] is not None

    detail = design_client.get("/api/v1/restaurants/r1")
    assert detail.status_code == 200
    assert detail.json()["name"] == "Spice Garden"

    popular = design_client.get("/api/v1/restaurants/popular", params={"location": "BTM"})
    assert popular.status_code == 200
    assert popular.json()["trending"]
