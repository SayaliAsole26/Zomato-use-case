#!/usr/bin/env python3
"""Phase 1 smoke test: load data and print summary."""

import logging
import sys
from pathlib import Path

# Allow running as: python scripts/smoke_data.py
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.repository import get_repository

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def main() -> None:
    repo = get_repository()
    records = repo.get_all()
    locations = repo.get_locations()

    print(f"Record count: {len(records)}")
    print(f"Unique locations: {len(locations)}")
    print(f"Sample locations: {locations[:10]}")
    if records:
        sample = records[0]
        print("\nSample record:")
        print(f"  id: {sample.id}")
        print(f"  name: {sample.name}")
        print(f"  location: {sample.location}")
        print(f"  cuisines: {sample.cuisines}")
        print(f"  rating: {sample.rating}")
        print(f"  cost_for_two: {sample.cost_for_two}")
        print(f"  cost_tier: {sample.cost_tier}")


if __name__ == "__main__":
    main()
