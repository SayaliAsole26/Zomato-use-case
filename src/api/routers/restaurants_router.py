"""Restaurant routes (design/backend.md)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.deps import get_repository_dep
from src.api.restaurant_service import (
    get_restaurant,
    list_restaurants,
    popular_restaurants,
    search_restaurants,
)
from src.api.schemas import PopularRestaurantsResponse, RestaurantDetail, RestaurantListResponse
from src.data.repository import RestaurantRepository
from src.models.preferences import Budget

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.get("", response_model=RestaurantListResponse)
def list_all_restaurants(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    repo: RestaurantRepository = Depends(get_repository_dep),
) -> RestaurantListResponse:
    items, total = list_restaurants(repo.get_all(), limit=limit, offset=offset)
    return RestaurantListResponse(restaurants=items, total=total, limit=limit, offset=offset)


@router.get("/search", response_model=RestaurantListResponse)
def search(
    location: str | None = None,
    cuisine: str | None = None,
    budget: Budget | None = None,
    min_rating: float | None = Query(None, ge=0, le=5),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    repo: RestaurantRepository = Depends(get_repository_dep),
) -> RestaurantListResponse:
    items, total = search_restaurants(
        repo.get_all(),
        location=location,
        cuisine=cuisine,
        budget=budget,
        min_rating=min_rating,
        limit=limit,
        offset=offset,
    )
    return RestaurantListResponse(restaurants=items, total=total, limit=limit, offset=offset)


@router.get("/popular", response_model=PopularRestaurantsResponse)
def popular(
    location: str | None = None,
    limit: int = Query(6, ge=1, le=20),
    repo: RestaurantRepository = Depends(get_repository_dep),
) -> PopularRestaurantsResponse:
    return PopularRestaurantsResponse(
        trending=popular_restaurants(repo.get_all(), location=location, category="trending", limit=limit),
        highly_rated=popular_restaurants(
            repo.get_all(), location=location, category="highly_rated", limit=limit
        ),
        new_opening=popular_restaurants(
            repo.get_all(), location=location, category="new_opening", limit=limit
        ),
    )


@router.get("/{restaurant_id}", response_model=RestaurantDetail)
def get_by_id(
    restaurant_id: str,
    repo: RestaurantRepository = Depends(get_repository_dep),
) -> RestaurantDetail:
    record = repo.get_by_id(restaurant_id)
    summary = get_restaurant(record)
    if summary is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return RestaurantDetail(**summary)
