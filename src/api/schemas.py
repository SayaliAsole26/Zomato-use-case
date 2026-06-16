"""HTTP request/response models for the REST API."""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.models.recommendation import RecommendationItem, RecommendationMeta


class RecommendationApiResponse(BaseModel):
    """Unified API response for success and empty-filter cases (architecture §6.1)."""

    summary: str | None = Field(None, description="Optional summary from LLM")
    recommendations: list[RecommendationItem] = Field(
        default_factory=list,
        description="Ranked recommendations; empty when no restaurants match filters",
    )
    meta: RecommendationMeta | None = Field(None, description="Process metadata")
    message: str | None = Field(
        None,
        description="Present when no restaurants match; explains empty result",
    )
    suggestions: list[str] | None = Field(
        None,
        description="Broadening suggestions when recommendations is empty",
    )


class HealthResponse(BaseModel):
    """Health check payload including dataset readiness."""

    status: str = Field(..., description="ok when dataset loaded, degraded otherwise")
    dataset_loaded: bool = Field(..., description="True when restaurant records are available")
    restaurant_count: int = Field(..., ge=0, description="Number of loaded restaurant records")


class LocationsResponse(BaseModel):
    """Known restaurant locations for UI dropdowns."""

    locations: list[str] = Field(..., description="Sorted unique location names from dataset")


class RestaurantSummary(BaseModel):
    id: str
    name: str
    cuisine: str
    location: str
    rating: float | None = None
    price_range: str | None = None
    estimated_cost: str | None = None
    votes: int | None = None
    address: str | None = None
    match_score: float | None = None


class RestaurantDetail(RestaurantSummary):
    pass


class RestaurantListResponse(BaseModel):
    restaurants: list[RestaurantSummary]
    total: int
    limit: int
    offset: int


class PopularRestaurantsResponse(BaseModel):
    trending: list[RestaurantSummary]
    highly_rated: list[RestaurantSummary]
    new_opening: list[RestaurantSummary]
