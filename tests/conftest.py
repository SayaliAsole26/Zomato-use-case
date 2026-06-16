import pandas as pd
import pytest

from src.config.settings import Settings


@pytest.fixture
def test_settings(tmp_path) -> Settings:
    return Settings(
        data_cache_path=tmp_path / "restaurants.parquet",
        cost_tier_low_max=500,
        cost_tier_medium_max=1000,
        hf_load_max_retries=1,
        max_results=5,
        max_candidates_for_llm=30,
    )


@pytest.fixture
def sample_raw_df() -> pd.DataFrame:
    """Minimal raw HF-shaped dataframe for preprocessor tests."""
    return pd.DataFrame(
        [
            {
                "name": "Test Bistro",
                "location": "bangalore",
                "cuisines": "Italian, North Indian",
                "rate": "4.5/5",
                "votes": 120,
                "address": "123 MG Road",
                "approx_cost(for two people)": "800",
                "listed_in(city)": "Bangalore",
            },
            {
                "name": "Budget Eats",
                "location": "New Delhi",
                "cuisines": "Chinese",
                "rate": "NEW",
                "votes": 0,
                "address": None,
                "approx_cost(for two people)": "300",
                "listed_in(city)": "New Delhi",
            },
            {
                "name": "",
                "location": "Mumbai",
                "cuisines": "Cafe",
                "rate": "3.8/5",
                "votes": 10,
                "address": "X",
                "approx_cost(for two people)": "1,500",
                "listed_in(city)": "Mumbai",
            },
            {
                "name": "Duplicate Place",
                "location": "Bangalore",
                "cuisines": "Cafe",
                "rate": "4.0/5",
                "votes": 50,
                "address": "A",
                "approx_cost(for two people)": "600",
                "listed_in(city)": "Bangalore",
            },
            {
                "name": "Duplicate Place",
                "location": "bangalore",
                "cuisines": "Cafe",
                "rate": "4.2/5",
                "votes": 60,
                "address": "B",
                "approx_cost(for two people)": "600",
                "listed_in(city)": "Bangalore",
            },
        ]
    )
