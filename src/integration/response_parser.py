"""Parse and validate LLM responses for restaurant recommendations."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from src.models.recommendation import (
    EmptyResult,
    RecommendationItem,
    RecommendationMeta,
    RecommendationResponse,
)
from src.models.restaurant import RestaurantRecord

logger = logging.getLogger(__name__)


def parse_response(
    raw_response: str,
    candidates: list[RestaurantRecord],
    max_results: int = 5,
) -> RecommendationResponse:
    """
    Parse LLM response and validate against candidate set.
    
    Args:
        raw_response: Raw text response from LLM
        candidates: List of candidate restaurant records
        max_results: Maximum number of results to return
        
    Returns:
        Parsed and validated RecommendationResponse
        
    Raises:
        ValueError: If response cannot be parsed or validated
    """
    try:
        # Try to extract JSON from response (handle markdown code blocks)
        json_str = _extract_json(raw_response)
        data = json.loads(json_str)
        
        # Validate structure
        if not isinstance(data, dict):
            raise ValueError("Response must be a JSON object")
        
        # Parse summary
        summary = data.get("summary")
        if summary is not None and not isinstance(summary, str):
            logger.warning("Summary is not a string, ignoring")
            summary = None
        
        # Parse recommendations
        recommendations_data = data.get("recommendations", [])
        if not isinstance(recommendations_data, list):
            raise ValueError("recommendations must be a list")
        
        # Build candidate lookup
        candidate_map = {r.id: r for r in candidates}
        
        # Parse and validate each recommendation
        recommendations: list[RecommendationItem] = []
        seen_ids: set[str] = set()
        for rec_data in recommendations_data:
            try:
                item = _parse_recommendation_item(rec_data, candidate_map)
                if item.restaurant_id in seen_ids:
                    logger.warning(
                        "Skipping duplicate restaurant_id in LLM output: %s",
                        item.restaurant_id,
                    )
                    continue
                seen_ids.add(item.restaurant_id)
                recommendations.append(item)
            except ValueError as exc:
                logger.warning("Skipping invalid recommendation: %s", exc)

        if recommendations_data and not recommendations:
            raise ValueError("No valid recommendations in LLM response")

        # Sort by rank
        recommendations.sort(key=lambda x: x.rank)
        
        # Cap to max_results
        recommendations = recommendations[:max_results]
        
        return RecommendationResponse(
            summary=summary,
            recommendations=recommendations,
            meta=None,  # Meta will be added by orchestrator
        )
        
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("Failed to parse LLM response: %s", exc)
        raise ValueError(f"Invalid LLM response: {exc}") from exc


def _extract_json(text: str) -> str:
    """Extract JSON from text, handling markdown code blocks."""
    # Try to find JSON in markdown code blocks
    json_pattern = re.compile(r'```(?:json)?\s*(\{.*?\})\s*```', re.DOTALL)
    match = json_pattern.search(text)
    if match:
        return match.group(1)
    
    # Try to find JSON object directly
    json_pattern = re.compile(r'\{.*\}', re.DOTALL)
    match = json_pattern.search(text)
    if match:
        return match.group(0)
    
    # Return as-is if no pattern matches
    return text


def _parse_recommendation_item(
    data: dict[str, Any],
    candidate_map: dict[str, RestaurantRecord],
) -> RecommendationItem:
    """Parse a single recommendation item and validate."""
    if not isinstance(data, dict):
        raise ValueError("Recommendation must be an object")
    
    restaurant_id = data.get("restaurant_id")
    if not restaurant_id or not isinstance(restaurant_id, str):
        raise ValueError("restaurant_id is required and must be a string")
    
    # Validate restaurant_id exists in candidates
    if restaurant_id not in candidate_map:
        raise ValueError(f"restaurant_id '{restaurant_id}' not found in candidate list")
    
    record = candidate_map[restaurant_id]
    
    rank = data.get("rank")
    if rank is None or not isinstance(rank, int) or rank < 1:
        raise ValueError("rank is required and must be a positive integer")
    
    explanation = data.get("explanation")
    if not explanation or not isinstance(explanation, str) or not explanation.strip():
        explanation = "Matches your preferences based on rating and cuisine."
    
    # Build estimated cost display
    estimated_cost = None
    if record.cost_for_two is not None:
        estimated_cost = f"₹{record.cost_for_two} for two"
    
    # Build cuisine display
    cuisine = ", ".join(record.cuisines) if record.cuisines else "Various"
    
    return RecommendationItem(
        restaurant_id=restaurant_id,
        name=record.name,
        cuisine=cuisine,
        rating=record.rating,
        estimated_cost=estimated_cost,
        explanation=explanation,
        rank=rank,
    )


def create_fallback_response(
    candidates: list[RestaurantRecord],
    max_results: int = 5,
) -> RecommendationResponse:
    """
    Create a fallback response when LLM fails.
    
    Returns top-K candidates by rating with generic explanations.
    
    Args:
        candidates: List of candidate restaurant records
        max_results: Maximum number of results to return
        
    Returns:
        RecommendationResponse with fallback recommendations
    """
    # Sort by rating (desc), then votes (desc)
    sorted_candidates = sorted(
        candidates,
        key=lambda r: (r.rating or 0, r.votes or 0),
        reverse=True,
    )
    
    # Take top K
    top_candidates = sorted_candidates[:max_results]
    
    # Build recommendations with generic explanations
    recommendations: list[RecommendationItem] = []
    for rank, record in enumerate(top_candidates, 1):
        estimated_cost = None
        if record.cost_for_two is not None:
            estimated_cost = f"₹{record.cost_for_two} for two"
        
        cuisine = ", ".join(record.cuisines) if record.cuisines else "Various"
        
        explanation = f"Highly rated restaurant with {cuisine} cuisine"
        if record.rating:
            explanation += f" and a rating of {record.rating}/5"
        
        recommendations.append(
            RecommendationItem(
                restaurant_id=record.id,
                name=record.name,
                cuisine=cuisine,
                rating=record.rating,
                estimated_cost=estimated_cost,
                explanation=explanation,
                rank=rank,
            )
        )
    
    return RecommendationResponse(
        summary=None,
        recommendations=recommendations,
        meta=None,
    )
