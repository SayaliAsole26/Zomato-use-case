#!/usr/bin/env python3
"""
Phase 4 manual integration test: prompt -> Groq -> parse with mock candidates.

Usage:
    python scripts/test_llm_pipeline.py
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config.settings import get_settings
from src.integration.prompt_builder import build_prompt
from src.integration.response_parser import create_fallback_response, parse_response
from src.llm.client import GroqClient
from src.models.preferences import Budget, UserPreferences
from src.models.restaurant import CostTier, RestaurantRecord

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _mock_candidates() -> list[RestaurantRecord]:
    return [
        RestaurantRecord(
            id="c1",
            name="Trattoria Roma",
            location="Bangalore",
            cuisines=["italian", "pizza"],
            rating=4.6,
            cost_for_two=900,
            cost_tier=CostTier.MEDIUM,
            votes=210,
        ),
        RestaurantRecord(
            id="c2",
            name="Dragon Wok",
            location="Bangalore",
            cuisines=["chinese", "asian"],
            rating=4.3,
            cost_for_two=700,
            cost_tier=CostTier.MEDIUM,
            votes=150,
        ),
        RestaurantRecord(
            id="c3",
            name="Spice Garden",
            location="Bangalore",
            cuisines=["north indian", "biryani"],
            rating=4.1,
            cost_for_two=650,
            cost_tier=CostTier.MEDIUM,
            votes=95,
        ),
        RestaurantRecord(
            id="c4",
            name="Cafe Milano",
            location="Bangalore",
            cuisines=["cafe", "italian"],
            rating=4.0,
            cost_for_two=500,
            cost_tier=CostTier.LOW,
            votes=80,
        ),
        RestaurantRecord(
            id="c5",
            name="Sushi Zen",
            location="Bangalore",
            cuisines=["japanese", "sushi"],
            rating=4.4,
            cost_for_two=1200,
            cost_tier=CostTier.HIGH,
            votes=60,
        ),
    ]


def main() -> int:
    settings = get_settings()
    if not settings.groq_api_key:
        print("ERROR: Set GROQ_API_KEY in .env before running this script.")
        return 1

    prefs = UserPreferences(
        location="Bangalore",
        budget=Budget.MEDIUM,
        cuisine="Italian",
        min_rating=4.0,
        additional=["family-friendly"],
        max_results=3,
    )
    candidates = _mock_candidates()

    print("Phase 4 LLM pipeline test")
    print("-" * 50)
    print(f"Model: {settings.llm_model}")
    print(f"Candidates: {len(candidates)}")

    system, user = build_prompt(prefs, candidates, max_results=3)
    client = GroqClient(settings=settings)

    print("Calling Groq...")
    raw = client.complete(system, user)
    print(f"Raw response length: {len(raw)} chars")

    try:
        result = parse_response(raw, candidates, max_results=3)
    except ValueError as exc:
        logger.warning("Parse failed (%s); using fallback", exc)
        result = create_fallback_response(candidates, max_results=3)

    print("\nParsed recommendations:")
    for item in result.recommendations:
        print(f"  #{item.rank} {item.name} ({item.restaurant_id})")
        print(f"     {item.cuisine} | rating={item.rating} | {item.estimated_cost}")
        print(f"     {item.explanation}")

    if result.summary:
        print(f"\nSummary: {result.summary}")

    payload = result.model_dump(mode="json")
    print("\nJSON output:")
    print(json.dumps(payload, indent=2))
    print("-" * 50)
    print("Phase 4 pipeline test complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
