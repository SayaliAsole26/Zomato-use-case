"""Load raw Zomato dataset from Hugging Face."""

from __future__ import annotations

import logging
import time

import pandas as pd
from datasets import load_dataset

from src.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)

HF_SPLIT = "train"


def load_raw_from_huggingface(
    *,
    settings: Settings | None = None,
) -> pd.DataFrame:
    """Download dataset from Hugging Face with retries (no local cache)."""
    settings = settings or get_settings()
    last_error: Exception | None = None
    max_retries = settings.hf_load_max_retries

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                "Loading %s from Hugging Face (attempt %d/%d)",
                settings.hf_dataset_name,
                attempt,
                max_retries,
            )
            ds = load_dataset(settings.hf_dataset_name, split=HF_SPLIT)
            logger.info("Raw columns: %s", ds.column_names)
            df = ds.to_pandas()
            if df.empty:
                raise RuntimeError("Dataset is empty after load (DATA-04)")
            return df
        except Exception as exc:
            last_error = exc
            logger.warning("HF load failed (attempt %d): %s", attempt, exc)
            if attempt < max_retries:
                time.sleep(2**attempt)

    raise RuntimeError(
        f"Failed to load dataset '{settings.hf_dataset_name}' after {max_retries} attempts"
    ) from last_error
