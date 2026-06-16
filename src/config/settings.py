from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    hf_dataset_name: str = Field(
        default="ManikaSaini/zomato-restaurant-recommendation",
        alias="HF_DATASET_NAME",
    )
    data_cache_path: Path = Field(
        default=PROJECT_ROOT / "data" / "cache" / "restaurants.parquet",
        alias="DATA_CACHE_PATH",
    )
    cost_tier_low_max: int = Field(default=500, alias="COST_TIER_LOW_MAX")
    cost_tier_medium_max: int = Field(default=1000, alias="COST_TIER_MEDIUM_MAX")
    hf_load_max_retries: int = Field(default=3, alias="HF_LOAD_MAX_RETRIES")
    
    # LLM configuration (Phase 4+)
    llm_model: str = Field(default="llama-3.3-70b-versatile", alias="LLM_MODEL")
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    max_candidates_for_llm: int = Field(default=30, alias="MAX_CANDIDATES_FOR_LLM")
    max_results: int = Field(default=5, alias="MAX_RESULTS")


@lru_cache
def get_settings() -> Settings:
    return Settings()
