#!/usr/bin/env python3
"""Run documented demo scenarios (Phase 7.7)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.logging_config import setup_logging
from src.models.preferences import Budget, UserPreferences
from src.models.recommendation import EmptyResult, RecommendationResponse
from src.models.restaurant import CostTier, RestaurantRecord
from src.orchestrator import recommend

MOCK_LLM_JSON = """{
  "summary": "Demo mock summary",
  "recommendations": [
    {
      "restaurant_id": "demo-1",
      "rank": 1,
      "explanation": "Demo explanation for manual QA"
    }
  ]
}"""


def _demo_candidates() -> list[RestaurantRecord]:
    return [
        RestaurantRecord(
            id="demo-1",
            name="Demo Restaurant",
            location="BTM",
            cuisines=["north indian"],
            rating=4.5,
            cost_for_two=800,
            cost_tier=CostTier.MEDIUM,
            votes=100,
        )
    ]


def _mock_repo(candidates: list[RestaurantRecord]) -> Mock:
    repo = Mock()
    repo.query.return_value = candidates
    repo.get_locations.return_value = ["BTM", "Banashankari"]
    return repo


def run_scenario(
    name: str,
    prefs: UserPreferences,
    *,
    live: bool,
    mock_empty: bool = False,
) -> None:
    print(f"\n=== {name} ===")
    print(f"location={prefs.location} budget={prefs.budget.value} cuisine={prefs.cuisine}")

    if live:
        result = recommend(prefs)
    else:
        candidates = [] if mock_empty else _demo_candidates()
        with patch("src.orchestrator.get_repository") as get_repo, patch(
            "src.orchestrator.GroqClient"
        ) as groq_cls:
            get_repo.return_value = _mock_repo(candidates)
            groq_cls.return_value.complete.return_value = MOCK_LLM_JSON
            result = recommend(prefs)

    if isinstance(result, EmptyResult):
        print("Result: EMPTY")
        print(result.message)
    elif isinstance(result, RecommendationResponse):
        print(f"Result: OK ({len(result.recommendations)} recommendations)")
        for item in result.recommendations:
            print(f"  - {item.name}: {item.explanation[:60]}...")
        if result.meta:
            print(f"  meta: candidates={result.meta.candidates_considered} fallback={result.meta.fallback}")


def main() -> int:
    setup_logging()
    parser = argparse.ArgumentParser(description="Run demo scenarios")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Call real Groq API (requires GROQ_API_KEY)",
    )
    args = parser.parse_args()

    run_scenario(
        "Scenario 1 - Happy path",
        UserPreferences(
            location="BTM",
            budget=Budget.MEDIUM,
            cuisine="North Indian",
            min_rating=4.0,
            max_results=3,
        ),
        live=args.live,
    )
    run_scenario(
        "Scenario 2 - Empty filters",
        UserPreferences(location="BTM", budget=Budget.LOW, min_rating=5.0),
        live=args.live,
        mock_empty=True,
    )

    print("\nDone. See docs/demo-scenarios.md for full manual checklist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
