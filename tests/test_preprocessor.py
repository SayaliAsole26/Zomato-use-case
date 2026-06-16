import pandas as pd

from src.data.preprocessor import (
    derive_cost_tier,
    parse_cost_for_two,
    parse_rating,
    preprocess_dataframe,
)
from src.models.restaurant import CostTier


def test_parse_rating_valid():
    assert parse_rating("4.5/5") == 4.5
    assert parse_rating("4.1/5") == 4.1


def test_parse_rating_invalid():
    assert parse_rating("NEW") is None
    assert parse_rating("-") is None
    assert parse_rating("99/5") is None
    assert parse_rating(None) is None


def test_parse_cost_for_two():
    assert parse_cost_for_two("800") == 800
    assert parse_cost_for_two("1,200") == 1200
    assert parse_cost_for_two("300-400") == 350


def test_derive_cost_tier():
    assert derive_cost_tier(400, low_max=500, medium_max=1000) == CostTier.LOW
    assert derive_cost_tier(800, low_max=500, medium_max=1000) == CostTier.MEDIUM
    assert derive_cost_tier(1500, low_max=500, medium_max=1000) == CostTier.HIGH
    assert derive_cost_tier(None, low_max=500, medium_max=1000) is None


def test_preprocess_dataframe(sample_raw_df, test_settings):
    records = preprocess_dataframe(sample_raw_df, settings=test_settings)

    assert len(records) == 3

    bistro = next(r for r in records if r.name == "Test Bistro")
    assert bistro.location == "Bangalore"
    assert bistro.cuisines == ["italian", "north indian"]
    assert bistro.rating == 4.5
    assert bistro.cost_for_two == 800
    assert bistro.cost_tier == CostTier.MEDIUM
    assert bistro.votes == 120
    assert bistro.id

    budget = next(r for r in records if r.name == "Budget Eats")
    assert budget.rating is None
    assert budget.cost_tier == CostTier.LOW

    names = [r.name for r in records]
    assert "Duplicate Place" in names
    assert names.count("Duplicate Place") == 1


def test_preprocess_drops_empty_name(sample_raw_df, test_settings):
    df = sample_raw_df[sample_raw_df["name"] != ""]
    records = preprocess_dataframe(df, settings=test_settings)
    assert all(r.name for r in records)
