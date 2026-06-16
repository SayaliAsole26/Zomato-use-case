"""FastAPI dependency injection helpers."""

from __future__ import annotations

from fastapi import Depends

from src.config.settings import Settings, get_settings
from src.data.repository import RestaurantRepository, get_repository
from src.llm.client import GroqClient, LLMClient


def get_settings_dep() -> Settings:
    return get_settings()


def get_repository_dep() -> RestaurantRepository:
    return get_repository()


def get_llm_client_dep(settings: Settings = Depends(get_settings_dep)) -> LLMClient:
    return GroqClient(settings=settings)
