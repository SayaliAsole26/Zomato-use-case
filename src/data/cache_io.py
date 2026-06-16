"""Persist and load preprocessed restaurant Parquet cache."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd

from src.models.restaurant import CostTier, RestaurantRecord

logger = logging.getLogger(__name__)


def save_processed_cache(records: list[RestaurantRecord], path: Path) -> None:
    rows = []
    for record in records:
        data = record.model_dump()
        data["cuisines"] = json.dumps(data["cuisines"])
        data.pop("raw", None)
        if data.get("cost_tier") is not None:
            data["cost_tier"] = data["cost_tier"].value
        rows.append(data)

    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(path, index=False)
    logger.info("Saved %d processed records to %s", len(records), path)


def load_processed_cache(path: Path) -> list[RestaurantRecord] | None:
    if not path.exists():
        return None
    try:
        df = pd.read_parquet(path)
    except Exception as exc:
        logger.warning("Invalid processed cache %s: %s", path, exc)
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        return None

    records: list[RestaurantRecord] = []
    for _, row in df.iterrows():
        cuisines = row["cuisines"]
        if isinstance(cuisines, str):
            cuisines = json.loads(cuisines)

        tier = row.get("cost_tier")
        cost_tier = CostTier(tier) if pd.notna(tier) and tier else None

        records.append(
            RestaurantRecord(
                id=str(row["id"]),
                name=str(row["name"]),
                location=str(row["location"]),
                cuisines=list(cuisines),
                rating=float(row["rating"]) if pd.notna(row.get("rating")) else None,
                cost_for_two=int(row["cost_for_two"])
                if pd.notna(row.get("cost_for_two"))
                else None,
                cost_tier=cost_tier,
                address=str(row["address"]) if pd.notna(row.get("address")) else None,
                votes=int(row["votes"]) if pd.notna(row.get("votes")) else None,
                raw=None,
            )
        )

    logger.info("Loaded %d records from processed cache", len(records))
    return records
