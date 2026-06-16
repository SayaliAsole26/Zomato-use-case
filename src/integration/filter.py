"""Candidate filter for restaurant recommendations."""

from __future__ import annotations

import logging

from src.config.settings import Settings, get_settings
from src.models.preferences import Budget, UserPreferences
from src.models.restaurant import RestaurantRecord

logger = logging.getLogger(__name__)


def filter_candidates(
    records: list[RestaurantRecord],
    prefs: UserPreferences,
    *,
    settings: Settings | None = None,
) -> list[RestaurantRecord]:
    """
    Filter restaurant records based on user preferences.

    Applies filters in order: location, budget, cuisine (optional), rating (optional).
    Then sorts by rating (desc) and votes (desc), and caps to MAX_CANDIDATES_FOR_LLM.

    Returns an empty list when nothing matches. Callers (orchestrator) must not
    invoke the LLM when the result is empty (Phase 3.9 short-circuit contract).

    Args:
        records: All restaurant records to filter
        prefs: User preferences for filtering
        settings: Application settings (uses default if None)

    Returns:
        Filtered, sorted, capped list of restaurant records (may be empty)
    """
    settings = settings or get_settings()
    input_count = len(records)

    filtered = _filter_by_location(records, prefs.location)
    filtered = _filter_by_budget(filtered, prefs.budget)

    if prefs.cuisine:
        filtered = _filter_by_cuisine(filtered, prefs.cuisine)

    if prefs.min_rating is not None:
        filtered = _filter_by_rating(filtered, prefs.min_rating)

    filtered = _sort_candidates(filtered)
    filtered = filtered[: settings.max_candidates_for_llm]

    logger.info(
        "filter.input_count=%d filter.output_count=%d location=%s budget=%s cuisine=%s min_rating=%s",
        input_count,
        len(filtered),
        prefs.location,
        prefs.budget.value,
        prefs.cuisine or "None",
        prefs.min_rating if prefs.min_rating is not None else "None",
    )

    return filtered


def _filter_by_location(
    records: list[RestaurantRecord],
    location: str,
) -> list[RestaurantRecord]:
    """Filter records by location (case-insensitive)."""
    target = location.lower().strip()
    return [r for r in records if r.location.lower().strip() == target]


def _filter_by_budget(
    records: list[RestaurantRecord],
    budget: Budget,
) -> list[RestaurantRecord]:
    """Filter records by cost tier matching user budget."""
    target = budget.value
    return [r for r in records if r.cost_tier is not None and r.cost_tier.value == target]


def _filter_by_cuisine(
    records: list[RestaurantRecord],
    cuisine: str,
) -> list[RestaurantRecord]:
    """
    Filter records by cuisine (substring match).

    Matches if any cuisine token contains the preference string (case-insensitive).
    """
    target = cuisine.lower().strip()
    return [r for r in records if any(target in c.lower() for c in r.cuisines)]


def _filter_by_rating(
    records: list[RestaurantRecord],
    min_rating: float,
) -> list[RestaurantRecord]:
    """Filter records by minimum rating (excludes null ratings)."""
    return [r for r in records if r.rating is not None and r.rating >= min_rating]


def _sort_candidates(records: list[RestaurantRecord]) -> list[RestaurantRecord]:
    """
    Sort candidates by rating (desc), then votes (desc).

    Records with missing rating are sorted last; stable order by name for ties.
    """

    def sort_key(record: RestaurantRecord) -> tuple:
        rating = record.rating if record.rating is not None else -1.0
        votes = record.votes if record.votes is not None else 0
        return (-rating, -votes, record.name.lower())

    return sorted(records, key=sort_key)
