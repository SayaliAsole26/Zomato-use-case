"""Map raw Hugging Face rows to canonical RestaurantRecord objects."""

from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Any

import pandas as pd

from src.config.settings import PROJECT_ROOT, Settings, get_settings
from src.data.cache_io import load_processed_cache, save_processed_cache
from src.data.loader import load_raw_from_huggingface
from src.models.restaurant import CostTier, RestaurantRecord

logger = logging.getLogger(__name__)

COL_NAME = "name"
COL_LOCATION = "location"
COL_CUISINES = "cuisines"
COL_RATE = "rate"
COL_VOTES = "votes"
COL_ADDRESS = "address"
COL_COST = "approx_cost(for two people)"
COL_LISTED_CITY = "listed_in(city)"

LOCATION_ALIASES: dict[str, str] = {
    "bengaluru": "Bangalore",
    "bangalore": "Bangalore",
    "bombay": "Mumbai",
    "mumbai": "Mumbai",
    "delhi": "New Delhi",
    "new delhi": "New Delhi",
    "gurgaon": "Gurugram",
    "gurugram": "Gurugram",
}

_CUISINE_SPLIT = re.compile(r"[,|/]")
_COST_DIGITS = re.compile(r"\d+")
_RATE_FRACTION = re.compile(r"(\d+(?:\.\d+)?)\s*/\s*5", re.IGNORECASE)
_RATE_PLAIN = re.compile(r"^(\d+(?:\.\d+)?)$")


def _normalize_location(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "-"}:
        return None
    key = text.lower()
    return LOCATION_ALIASES.get(key, text.title() if text.islower() else text)


def _split_cuisines(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none"}:
        return []
    parts = _CUISINE_SPLIT.split(text)
    return [p.strip().lower() for p in parts if p.strip()]


def parse_rating(value: Any) -> float | None:
    """Parse Zomato rate strings; invalid values return None (PRE-02)."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text or text.upper() in {"NEW", "-", "NAN"}:
        return None

    match = _RATE_FRACTION.search(text)
    if match:
        rating = float(match.group(1))
    else:
        plain = _RATE_PLAIN.match(text)
        if not plain:
            return None
        rating = float(plain.group(1))

    if rating < 0 or rating > 5:
        return None
    return round(rating, 2)


def parse_cost_for_two(value: Any) -> int | None:
    """Parse cost strings like '800', '1,200', '300-400'."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip().replace(",", "")
    if not text or text.lower() in {"nan", "none", "-"}:
        return None

    numbers = _COST_DIGITS.findall(text)
    if not numbers:
        return None

    values = [int(n) for n in numbers]
    if len(values) >= 2 and "-" in text:
        return int(sum(values[:2]) / 2)
    return values[0]


def derive_cost_tier(
    cost: int | None,
    *,
    low_max: int,
    medium_max: int,
) -> CostTier | None:
    if cost is None:
        return None
    if cost <= low_max:
        return CostTier.LOW
    if cost <= medium_max:
        return CostTier.MEDIUM
    return CostTier.HIGH


def _stable_id(name: str, location: str, address: str | None, index: int) -> str:
    payload = f"{name}|{location}|{address or ''}|{index}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _serialize_raw(value: Any) -> Any:
    if isinstance(value, float) and pd.isna(value):
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, AttributeError):
            pass
    return value


def _row_to_record(row: pd.Series, index: int, settings: Settings) -> RestaurantRecord | None:
    name = row.get(COL_NAME)
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return None
    name_str = str(name).strip()
    if not name_str:
        return None

    location = _normalize_location(row.get(COL_LOCATION))
    if not location:
        location = _normalize_location(row.get(COL_LISTED_CITY))
    if not location:
        return None

    address_val = row.get(COL_ADDRESS)
    address = None
    if address_val is not None and not (isinstance(address_val, float) and pd.isna(address_val)):
        address = str(address_val).strip() or None

    votes_val = row.get(COL_VOTES)
    votes: int | None = None
    if votes_val is not None and not (isinstance(votes_val, float) and pd.isna(votes_val)):
        try:
            votes = max(0, int(votes_val))
        except (TypeError, ValueError):
            votes = None

    cost = parse_cost_for_two(row.get(COL_COST))
    tier = derive_cost_tier(
        cost,
        low_max=settings.cost_tier_low_max,
        medium_max=settings.cost_tier_medium_max,
    )

    raw = {k: _serialize_raw(v) for k, v in row.items()}

    return RestaurantRecord(
        id=_stable_id(name_str, location, address, index),
        name=name_str,
        location=location,
        cuisines=_split_cuisines(row.get(COL_CUISINES)),
        rating=parse_rating(row.get(COL_RATE)),
        cost_for_two=cost,
        cost_tier=tier,
        address=address,
        votes=votes,
        raw=raw,
    )


def preprocess_dataframe(
    df: pd.DataFrame,
    *,
    settings: Settings | None = None,
) -> list[RestaurantRecord]:
    """Transform raw HF dataframe into deduplicated RestaurantRecord list."""
    settings = settings or get_settings()
    records: list[RestaurantRecord] = []
    seen_keys: set[tuple[str, str]] = set()
    dropped = 0

    for index, row in df.iterrows():
        record = _row_to_record(row, int(index), settings)
        if record is None:
            dropped += 1
            continue

        dedupe_key = (record.name.lower(), record.location.lower())
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        records.append(record)

    logger.info(
        "Preprocessed %d records (dropped %d invalid rows)",
        len(records),
        dropped,
    )

    if not records:
        raise RuntimeError("No valid restaurant records after preprocessing (DATA-04)")

    return records


def load_restaurant_records(
    *,
    settings: Settings | None = None,
    force_refresh: bool = False,
) -> list[RestaurantRecord]:
    """
    Load records from processed Parquet cache, or HF + preprocess on miss.

    On HF failure, falls back to stale processed cache if present (DATA-01).
    """
    import time

    settings = settings or get_settings()
    cache_path = _resolve_cache_path(settings.data_cache_path)
    start = time.perf_counter()

    if not force_refresh:
        cached = load_processed_cache(cache_path)
        if cached:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            logger.info(
                "dataset.load.source=cache record_count=%d duration_ms=%d",
                len(cached),
                elapsed_ms,
            )
            return cached

    try:
        df = load_raw_from_huggingface(settings=settings)
        records = preprocess_dataframe(df, settings=settings)
        save_processed_cache(records, cache_path)
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        logger.info(
            "dataset.load.source=huggingface record_count=%d duration_ms=%d",
            len(records),
            elapsed_ms,
        )
        return records
    except RuntimeError:
        cached = load_processed_cache(cache_path)
        if cached:
            logger.warning("Using processed cache after Hugging Face load failure")
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            logger.info(
                "dataset.load.source=stale_cache record_count=%d duration_ms=%d",
                len(cached),
                elapsed_ms,
            )
            return cached
        raise


def _resolve_cache_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path
