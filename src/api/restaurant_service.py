"""Restaurant listing, search, and ranking per design/backend.md."""

from __future__ import annotations

import math
from typing import Literal

from src.integration.filter import filter_candidates
from src.models.preferences import Budget, UserPreferences
from src.models.restaurant import CostTier, RestaurantRecord

PopularCategory = Literal["trending", "highly_rated", "new_opening"]


def _cost_display(record: RestaurantRecord) -> str | None:
    if record.cost_for_two is not None:
        return f"₹{record.cost_for_two} for two"
    if record.cost_tier is not None:
        return record.cost_tier.value.title()
    return None


def _price_range_label(tier: CostTier | None) -> str:
    mapping = {CostTier.LOW: "$", CostTier.MEDIUM: "$$", CostTier.HIGH: "$$$"}
    return mapping.get(tier, "$$") if tier else "$$"


def record_to_summary(record: RestaurantRecord, *, match_score: float | None = None) -> dict:
    return {
        "id": record.id,
        "name": record.name,
        "cuisine": ", ".join(record.cuisines) if record.cuisines else "Various",
        "location": record.location,
        "rating": record.rating,
        "price_range": _price_range_label(record.cost_tier),
        "estimated_cost": _cost_display(record),
        "votes": record.votes,
        "address": record.address,
        "match_score": round(match_score, 1) if match_score is not None else None,
    }


def compute_match_score(
    record: RestaurantRecord,
    *,
    cuisine: str | None = None,
    budget: Budget | None = None,
) -> float:
    """Weighted score from design/backend.md ranking formula."""
    cuisine_score = 0.0
    if cuisine:
        needle = cuisine.lower().strip()
        cuisine_score = (
            1.0
            if any(needle in c.lower() for c in record.cuisines)
            else 0.0
        )
    else:
        cuisine_score = 0.7

    rating_score = (record.rating or 0) / 5.0

    budget_score = 0.5
    if budget and record.cost_tier is not None:
        budget_score = 1.0 if record.cost_tier.value == budget.value else 0.3

    distance_score = 1.0
    behavior_score = min(1.0, math.log10((record.votes or 0) + 1) / 3)

    total = (
        0.35 * cuisine_score
        + 0.25 * rating_score
        + 0.20 * budget_score
        + 0.10 * distance_score
        + 0.10 * behavior_score
    )
    return round(total * 100, 1)


def list_restaurants(
    records: list[RestaurantRecord],
    *,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[dict], int]:
    sorted_records = sorted(
        records,
        key=lambda r: (r.rating or 0, r.votes or 0),
        reverse=True,
    )
    total = len(sorted_records)
    page = sorted_records[offset : offset + limit]
    return [record_to_summary(r) for r in page], total


def get_restaurant(record: RestaurantRecord | None) -> dict | None:
    if record is None:
        return None
    return record_to_summary(record)


def search_restaurants(
    records: list[RestaurantRecord],
    *,
    location: str | None = None,
    cuisine: str | None = None,
    budget: Budget | None = None,
    min_rating: float | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[dict], int]:
    if location:
        prefs = UserPreferences(
            location=location,
            budget=budget or Budget.MEDIUM,
            cuisine=cuisine,
            min_rating=min_rating,
        )
        filtered = filter_candidates(records, prefs)
    else:
        filtered = list(records)
        if cuisine:
            needle = cuisine.lower().strip()
            filtered = [
                r
                for r in filtered
                if any(needle in c.lower() for c in r.cuisines)
            ]
        if budget:
            filtered = [
                r
                for r in filtered
                if r.cost_tier is not None and r.cost_tier.value == budget.value
            ]
        if min_rating is not None:
            filtered = [r for r in filtered if (r.rating or 0) >= min_rating]
        filtered = sorted(filtered, key=lambda r: (r.rating or 0, r.votes or 0), reverse=True)

    scored = [
        record_to_summary(
            r,
            match_score=compute_match_score(r, cuisine=cuisine, budget=budget),
        )
        for r in filtered
    ]
    total = len(scored)
    return scored[offset : offset + limit], total


def popular_restaurants(
    records: list[RestaurantRecord],
    *,
    location: str | None = None,
    category: PopularCategory = "trending",
    limit: int = 6,
) -> list[dict]:
    pool = records
    if location:
        target = location.lower().strip()
        pool = [r for r in records if r.location.lower().strip() == target]

    if category == "highly_rated":
        ranked = sorted(pool, key=lambda r: (r.rating or 0, r.votes or 0), reverse=True)
    elif category == "new_opening":
        ranked = sorted(pool, key=lambda r: r.votes or 0)
    else:
        ranked = sorted(pool, key=lambda r: (r.votes or 0, r.rating or 0), reverse=True)

    return [
        record_to_summary(r, match_score=compute_match_score(r))
        for r in ranked[:limit]
    ]
