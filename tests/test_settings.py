"""Tests for application settings."""

import pytest

from src.config.settings import Settings, get_settings

ENV_KEYS = (
    "GROQ_API_KEY",
    "LLM_MODEL",
    "MAX_RESULTS",
    "MAX_CANDIDATES_FOR_LLM",
    "HF_DATASET_NAME",
)


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def clean_env(monkeypatch):
    """Remove env vars so Settings uses field defaults only."""
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_settings_defaults(clean_env, tmp_path):
    settings = Settings(_env_file=tmp_path / "missing.env")
    assert settings.hf_dataset_name == "ManikaSaini/zomato-restaurant-recommendation"
    assert settings.cost_tier_low_max == 500
    assert settings.cost_tier_medium_max == 1000
    assert settings.max_candidates_for_llm == 30
    assert settings.max_results == 5
    assert settings.groq_api_key is None


def test_settings_load_from_env(clean_env, tmp_path):
    import os

    os.environ["MAX_RESULTS"] = "8"
    os.environ["MAX_CANDIDATES_FOR_LLM"] = "25"
    os.environ["GROQ_API_KEY"] = "test-key-not-real"
    os.environ["LLM_MODEL"] = "test-model"

    settings = Settings(_env_file=tmp_path / "missing.env")

    assert settings.max_results == 8
    assert settings.max_candidates_for_llm == 25
    assert settings.groq_api_key == "test-key-not-real"
    assert settings.llm_model == "test-model"


def test_get_settings_is_cached():
    first = get_settings()
    second = get_settings()
    assert first is second
