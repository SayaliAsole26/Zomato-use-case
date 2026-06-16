"""User preference models and validation."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator

from src.config.settings import Settings, get_settings


class Budget(str, Enum):
    """Budget tier for restaurant filtering."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UserPreferences(BaseModel):
    """User preferences for restaurant recommendations."""

    location: str = Field(..., description="City or area to search in")
    budget: Budget = Field(..., description="Budget tier (low, medium, high)")
    cuisine: str | None = Field(None, description="Optional primary cuisine preference")
    min_rating: float | None = Field(None, description="Minimum rating (0-5)")
    additional: list[str] = Field(default_factory=list, description="Additional preferences/tags")
    max_results: int | None = Field(None, ge=1, le=20, description="Maximum results to return")

    @field_validator("location")
    @classmethod
    def location_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("location cannot be empty")
        return v.strip()

    @field_validator("cuisine")
    @classmethod
    def cuisine_must_not_be_blank(cls, v: str | None) -> str | None:
        if v is None:
            return None
        stripped = v.strip()
        return stripped if stripped else None

    @field_validator("min_rating")
    @classmethod
    def rating_must_be_valid(cls, v: float | None) -> float | None:
        if v is not None and (v < 0 or v > 5):
            raise ValueError("rating must be between 0 and 5")
        return v

    @field_validator("additional")
    @classmethod
    def additional_tags_trimmed(cls, v: list[str]) -> list[str]:
        return [tag.strip() for tag in v if tag and tag.strip()]


def resolve_max_results(
    prefs: UserPreferences,
    *,
    settings: Settings | None = None,
) -> int:
    """Return effective max_results, defaulting to settings.MAX_RESULTS (5)."""
    if prefs.max_results is not None:
        return prefs.max_results
    settings = settings or get_settings()
    return settings.max_results


def validate_preferences(
    prefs: UserPreferences,
    known_locations: list[str] | None = None,
) -> tuple[bool, list[str]]:
    """
    Validate user preferences against known locations.

    Returns:
        Tuple of (is_valid, warning_messages)
    """
    warnings: list[str] = []

    if known_locations:
        normalized_input = prefs.location.lower().strip()
        normalized_known = [loc.lower().strip() for loc in known_locations]

        if normalized_input not in normalized_known:
            warnings.append(
                f"Location '{prefs.location}' not found in known locations. "
                "Results may be empty."
            )

    return True, warnings
