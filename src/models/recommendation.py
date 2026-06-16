"""Recommendation result models for orchestrator output."""

from __future__ import annotations

from typing import Union

from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    """A single restaurant recommendation with LLM-generated explanation."""

    restaurant_id: str = Field(..., description="Unique restaurant identifier")
    name: str = Field(..., description="Restaurant name")
    cuisine: str = Field(..., description="Cuisine type(s)")
    rating: float | None = Field(None, description="Restaurant rating (0-5)")
    estimated_cost: str | None = Field(None, description="Estimated cost display string")
    explanation: str = Field(..., description="AI-generated explanation for this recommendation")
    rank: int = Field(..., ge=1, description="Rank in recommendations (1-based)")


class EmptyResult(BaseModel):
    """Result when no restaurants match the user's preferences."""

    message: str = Field(
        default="No restaurants match your preferences. Try broadening your filters.",
        description="User-friendly message explaining why no results were found"
    )
    suggestions: list[str] = Field(
        default_factory=lambda: [
            "Try a different location",
            "Adjust your budget tier",
            "Remove cuisine filter",
            "Lower minimum rating"
        ],
        description="Suggestions for the user to try"
    )


class RecommendationMeta(BaseModel):
    """Metadata about the recommendation process."""

    candidates_considered: int = Field(..., description="Number of candidates sent to LLM")
    latency_ms: int | None = Field(None, description="Total latency in milliseconds")
    fallback: bool = Field(
        default=False,
        description="True when rating-based fallback was used instead of LLM output",
    )


class RecommendationResponse(BaseModel):
    """Full recommendation response from the orchestrator."""

    summary: str | None = Field(None, description="Optional summary from LLM")
    recommendations: list[RecommendationItem] = Field(
        default_factory=list,
        description="List of ranked restaurant recommendations",
    )
    meta: RecommendationMeta | None = Field(None, description="Process metadata")


RecommendationResult = Union[RecommendationResponse, EmptyResult]
