#!/usr/bin/env python3
"""Phase 5 smoke test: full recommend() pipeline with real data + Groq."""

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config.settings import get_settings
from src.data.repository import get_repository
from src.models.preferences import Budget, UserPreferences
from src.models.recommendation import EmptyResult, RecommendationResponse
from src.orchestrator import recommend

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def main() -> int:
    settings = get_settings()
    if not settings.groq_api_key:
        print("ERROR: Set GROQ_API_KEY in .env")
        return 1

    repo = get_repository()
    locations = repo.get_locations()
    if not locations:
        print("ERROR: No locations in repository")
        return 1

    # Pick first location that has medium-tier restaurants
    location = locations[0]
    for loc in locations[:20]:
        prefs_probe = UserPreferences(location=loc, budget=Budget.MEDIUM)
        if repo.query(prefs_probe):
            location = loc
            break

    prefs = UserPreferences(
        location=location,
        budget=Budget.MEDIUM,
        min_rating=3.5,
        max_results=3,
    )

    print(f"Running recommend() for location={location}, budget=medium")
    result = recommend(prefs)

    if isinstance(result, EmptyResult):
        print(result.message)
        return 0

    assert isinstance(result, RecommendationResponse)
    print(f"Summary: {result.summary or '(none)'}")
    print(f"Recommendations: {len(result.recommendations)}")
    for item in result.recommendations:
        print(f"  #{item.rank} {item.name} - {item.explanation[:80]}...")
    if result.meta:
        print(
            f"Meta: candidates={result.meta.candidates_considered}, "
            f"latency={result.meta.latency_ms}ms, fallback={result.meta.fallback}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
