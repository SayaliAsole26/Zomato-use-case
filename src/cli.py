"""CLI entry point for restaurant recommendation system."""

import argparse
import json
import sys

from src.logging_config import setup_logging
from src.models.preferences import Budget, UserPreferences
from src.models.recommendation import EmptyResult, RecommendationResponse
from src.orchestrator import recommend


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Get restaurant recommendations based on preferences",
    )
    parser.add_argument("--location", required=True, help="City or area to search in")
    parser.add_argument(
        "--budget",
        required=True,
        choices=["low", "medium", "high"],
        help="Budget tier",
    )
    parser.add_argument("--cuisine", help="Optional cuisine preference")
    parser.add_argument("--min-rating", type=float, help="Minimum rating (0-5)")
    parser.add_argument(
        "--max-results",
        type=int,
        default=None,
        help="Maximum number of results (default from MAX_RESULTS in .env)",
    )
    parser.add_argument("--additional", nargs="+", help="Additional preferences/tags")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for restaurant recommendations."""
    setup_logging()
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    args = build_parser().parse_args(argv)

    prefs = UserPreferences(
        location=args.location,
        budget=Budget(args.budget),
        cuisine=args.cuisine,
        min_rating=args.min_rating,
        additional=args.additional or [],
        max_results=args.max_results,
    )

    print(f"Getting recommendations for: {args.location}, {args.budget} budget...")

    try:
        result = recommend(prefs)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result.model_dump(mode="json"), indent=2))
    else:
        print_recommendations(result)
    return 0


def print_recommendations(result: RecommendationResponse | EmptyResult) -> None:
    """Print recommendations in a human-readable format."""
    if isinstance(result, EmptyResult):
        print("\n" + "=" * 50)
        print(result.message)
        print("\nSuggestions:")
        for suggestion in result.suggestions:
            print(f"  - {suggestion}")
        print("=" * 50)
        return

    print("\n" + "=" * 50)
    if result.summary:
        print(f"Summary: {result.summary}")
        print()

    print(f"Recommendations ({len(result.recommendations)}):")
    print()

    for item in result.recommendations:
        print(f"{item.rank}. {item.name}")
        print(f"   Cuisine: {item.cuisine}")
        if item.rating is not None:
            print(f"   Rating: {item.rating}/5")
        if item.estimated_cost:
            print(f"   Cost: {item.estimated_cost}")
        print(f"   Why: {item.explanation}")
        print()

    if result.meta:
        print("-" * 50)
        print(f"Candidates considered: {result.meta.candidates_considered}")
        if result.meta.latency_ms is not None:
            print(f"Latency: {result.meta.latency_ms}ms")
        if result.meta.fallback:
            print("Note: Showing rating-based picks (AI unavailable or parse failed)")
    print("=" * 50)


if __name__ == "__main__":
    sys.exit(main())
