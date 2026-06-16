"""Prompt builder for LLM restaurant ranking."""

from __future__ import annotations

from src.models.preferences import UserPreferences
from src.models.restaurant import RestaurantRecord


def build_prompt(
    prefs: UserPreferences,
    candidates: list[RestaurantRecord],
    max_results: int = 5,
) -> tuple[str, str]:
    """
    Build system and user prompts for LLM ranking.
    
    Args:
        prefs: User preferences
        candidates: Filtered restaurant candidates
        max_results: Maximum number of recommendations to return
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system_prompt = _build_system_prompt(max_results)
    user_prompt = _build_user_prompt(prefs, candidates, max_results)
    
    return system_prompt, user_prompt


def _build_system_prompt(max_results: int) -> str:
    """Build the system prompt with role and constraints."""
    return f"""You are an expert restaurant recommendation assistant. Your task is to rank restaurants based on user preferences and provide personalized explanations.

IMPORTANT CONSTRAINTS:
- ONLY recommend restaurants from the provided list. Do not invent or suggest restaurants not in the list.
- Return your response as valid JSON only, with no additional text or markdown formatting.
- Rank the top {max_results} restaurants that best match the user's preferences.
- Provide a brief explanation for each recommendation explaining why it fits the user's needs.
- Optionally provide a one-sentence summary of your overall recommendations.

JSON Schema:
{{
  "summary": "Optional one-sentence summary of the recommendations (string or null)",
  "recommendations": [
    {{
      "restaurant_id": "The exact restaurant_id from the provided list",
      "rank": 1,
      "explanation": "Why this restaurant fits the user's preferences"
    }}
  ]
}}"""


def _build_user_prompt(
    prefs: UserPreferences,
    candidates: list[RestaurantRecord],
    max_results: int,
) -> str:
    """Build the user prompt with preferences and candidate list."""
    # Build preferences section
    prefs_text = f"""User Preferences:
- Location: {prefs.location}
- Budget: {prefs.budget.value}
"""
    if prefs.cuisine:
        prefs_text += f"- Cuisine: {prefs.cuisine}\n"
    if prefs.min_rating is not None:
        prefs_text += f"- Minimum Rating: {prefs.min_rating}\n"
    if prefs.additional:
        prefs_text += f"- Additional preferences: {', '.join(prefs.additional)}\n"
    prefs_text += f"- Maximum results: {max_results}\n"
    
    # Build candidates section
    candidates_text = "Available Restaurants:\n"
    for i, candidate in enumerate(candidates, 1):
        candidates_text += f"\n{i}. ID: {candidate.id}\n"
        candidates_text += f"   Name: {candidate.name}\n"
        candidates_text += f"   Location: {candidate.location}\n"
        candidates_text += f"   Cuisines: {', '.join(candidate.cuisines)}\n"
        if candidate.rating is not None:
            candidates_text += f"   Rating: {candidate.rating}/5\n"
        if candidate.cost_for_two is not None:
            candidates_text += f"   Cost for two: ₹{candidate.cost_for_two}\n"
        if candidate.cost_tier is not None:
            candidates_text += f"   Cost tier: {candidate.cost_tier.value}\n"
    
    # Build task instruction
    task_text = f"""
Task:
Based on the user's preferences and the available restaurants above, rank the top {max_results} restaurants that best match the user's needs.

For each recommendation:
1. Use the exact restaurant_id from the list above
2. Assign a rank (1 = best match)
3. Provide a personalized explanation considering their location, budget, cuisine preference, rating, and any additional preferences

Return your response as valid JSON following the schema provided in the system prompt."""
    
    return f"{prefs_text}\n{candidates_text}\n{task_text}"
