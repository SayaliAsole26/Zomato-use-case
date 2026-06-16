"""Application orchestrator for restaurant recommendations."""

from __future__ import annotations

import logging
import time
import uuid

from src.config.settings import Settings, get_settings
from src.data.repository import RestaurantRepository, get_repository
from src.integration.prompt_builder import build_prompt
from src.integration.response_parser import create_fallback_response, parse_response
from src.llm.client import GroqClient, LLMClient
from src.models.preferences import UserPreferences, resolve_max_results, validate_preferences
from src.models.recommendation import (
    EmptyResult,
    RecommendationMeta,
    RecommendationResponse,
    RecommendationResult,
)

logger = logging.getLogger(__name__)


def recommend(
    prefs: UserPreferences,
    *,
    repository: RestaurantRepository | None = None,
    llm_client: LLMClient | None = None,
    settings: Settings | None = None,
) -> RecommendationResult:
    """
    Main recommendation pipeline (architecture section 4):

    1. validate(preferences)
    2. candidates = filter(store, preferences)
    3. if candidates.is_empty(): return EmptyResult
    4. prompt = build_prompt(preferences, candidates)
    5. raw = llm_client.complete(prompt)
    6. parsed = parse_response(raw, candidates)
    7. return enrich(parsed, candidates) with meta
    """
    request_id = str(uuid.uuid4())[:8]
    start_time = time.perf_counter()
    settings = settings or get_settings()
    max_results = resolve_max_results(prefs, settings=settings)

    logger.info("recommendation.request_id=%s starting pipeline", request_id)

    try:
        # Step 1: Validate preferences
        repo = repository or get_repository()
        is_valid, warnings = validate_preferences(prefs, repo.get_locations())
        if not is_valid:
            raise ValueError(f"Invalid preferences: {warnings}")

        for warning in warnings:
            logger.warning("recommendation.request_id=%s validation: %s", request_id, warning)

        # Step 2: Filter candidates
        candidates = repo.query(prefs)
        logger.info(
            "recommendation.request_id=%s candidates=%d",
            request_id,
            len(candidates),
        )

        # Step 3: Short-circuit when empty (no LLM call)
        if not candidates:
            logger.info("recommendation.request_id=%s empty result, skipping LLM", request_id)
            return EmptyResult()

        # Step 4: Build prompt
        system_prompt, user_prompt = build_prompt(prefs, candidates, max_results=max_results)

        # Step 5: Call LLM
        client = llm_client or GroqClient(settings=settings)
        used_fallback = False
        try:
            raw_response = client.complete(system_prompt, user_prompt)
            logger.info(
                "recommendation.request_id=%s llm.response_length=%d",
                request_id,
                len(raw_response),
            )
        except Exception as exc:
            logger.error("recommendation.request_id=%s llm failed: %s", request_id, exc)
            used_fallback = True
            response = create_fallback_response(candidates, max_results=max_results)
            response.meta = _build_meta(
                candidates_count=len(candidates),
                start_time=start_time,
                fallback=used_fallback,
            )
            return response

        # Step 6: Parse response
        try:
            response = parse_response(raw_response, candidates, max_results=max_results)
        except ValueError as exc:
            logger.error("recommendation.request_id=%s parse failed: %s", request_id, exc)
            used_fallback = True
            response = create_fallback_response(candidates, max_results=max_results)

        # Step 7: Attach meta
        response.meta = _build_meta(
            candidates_count=len(candidates),
            start_time=start_time,
            fallback=used_fallback,
        )
        logger.info("recommendation.request_id=%s completed", request_id)
        return response

    except Exception as exc:
        logger.error("recommendation.request_id=%s pipeline failed: %s", request_id, exc)
        raise


def _build_meta(
    *,
    candidates_count: int,
    start_time: float,
    fallback: bool,
) -> RecommendationMeta:
    latency_ms = int((time.perf_counter() - start_time) * 1000)
    return RecommendationMeta(
        candidates_considered=candidates_count,
        latency_ms=latency_ms,
        fallback=fallback,
    )
