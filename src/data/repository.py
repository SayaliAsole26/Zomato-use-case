"""In-memory restaurant repository."""

from __future__ import annotations

import logging
from functools import lru_cache

from src.data.preprocessor import load_restaurant_records
from src.integration.filter import filter_candidates
from src.models.preferences import UserPreferences
from src.models.restaurant import RestaurantRecord

logger = logging.getLogger(__name__)


class RestaurantRepository:
    """Read-only store of preprocessed restaurant records."""

    def __init__(self, records: list[RestaurantRecord]) -> None:
        self._records = records
        self._by_id = {r.id: r for r in records}

    def get_all(self) -> list[RestaurantRecord]:
        return list(self._records)

    def get_by_id(self, restaurant_id: str) -> RestaurantRecord | None:
        return self._by_id.get(restaurant_id)

    def get_locations(self) -> list[str]:
        return sorted({r.location for r in self._records})

    def get_by_filters(self, **kwargs) -> list[RestaurantRecord]:
        """Stub method to return records filtered by basic attributes."""
        location = kwargs.get("location")
        if location:
            return [r for r in self._records if r.location.lower() == location.lower()]
        return list(self._records)

    def count(self) -> int:
        return len(self._records)

    def query(self, prefs: UserPreferences) -> list[RestaurantRecord]:
        """
        Query repository with user preferences via the candidate filter.

        Returns a filtered, sorted, capped list. An empty list means no matches;
        the orchestrator must short-circuit and skip the LLM call.
        """
        return filter_candidates(self._records, prefs)


@lru_cache
def get_repository(*, force_refresh: bool = False) -> RestaurantRepository:
    """Singleton repository; loads data on first call."""
    records = load_restaurant_records(force_refresh=force_refresh)
    logger.info("Repository ready with %d records", len(records))
    return RestaurantRepository(records)


def build_repository_from_records(records: list[RestaurantRecord]) -> RestaurantRepository:
    """Build repository from an in-memory list (used in tests)."""
    return RestaurantRepository(records)
