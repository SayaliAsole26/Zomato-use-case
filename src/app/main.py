"""Streamlit presentation layer for restaurant recommendations."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Streamlit runs this file directly; ensure project root is on sys.path.
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from src.logging_config import setup_logging
from src.data.repository import get_repository
from src.models.preferences import Budget, UserPreferences
from src.models.recommendation import EmptyResult, RecommendationResponse
from src.orchestrator import recommend

logger = logging.getLogger(__name__)

BUDGET_OPTIONS = {
    "Low": Budget.LOW,
    "Medium": Budget.MEDIUM,
    "High": Budget.HIGH,
}

DEMO_LOCATION = "BTM"


def _configure_utf8_stdio() -> None:
    """Avoid UnicodeEncodeError for rupee symbol on Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def _location_index(locations: list[str], preferred: str = DEMO_LOCATION) -> int:
    try:
        return locations.index(preferred)
    except ValueError:
        return 0


@st.cache_resource(show_spinner="Loading restaurant dataset...")
def _cached_repository():
    return get_repository()


def parse_additional_tags(text: str) -> list[str]:
    """Split comma or newline separated tags into a trimmed list."""
    if not text or not text.strip():
        return []
    parts: list[str] = []
    for line in text.replace(",", "\n").splitlines():
        tag = line.strip()
        if tag:
            parts.append(tag)
    return parts


def build_preferences_from_form(
    *,
    location: str,
    budget_label: str,
    cuisine: str,
    min_rating: float,
    additional_text: str,
    max_results: int,
) -> UserPreferences:
    return UserPreferences(
        location=location,
        budget=BUDGET_OPTIONS[budget_label],
        cuisine=cuisine.strip() or None,
        min_rating=min_rating if min_rating > 0 else None,
        additional=parse_additional_tags(additional_text),
        max_results=max_results,
    )


def render_empty_state(result: EmptyResult) -> None:
    st.warning(result.message)
    st.markdown("**Try one of these:**")
    for tip in result.suggestions:
        st.markdown(f"- {tip}")


def render_recommendations(result: RecommendationResponse) -> None:
    if result.meta and result.meta.fallback:
        st.info(
            "Showing top-rated matches from your filters "
            "(AI was unavailable or returned an invalid response)."
        )

    if result.summary:
        st.success(result.summary)

    if not result.recommendations:
        st.warning("No recommendations to display.")
        return

    for item in result.recommendations:
        with st.container(border=True):
            st.subheader(f"#{item.rank} {item.name}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Cuisine", item.cuisine)
            col2.metric("Rating", f"{item.rating}/5" if item.rating is not None else "N/A")
            col3.metric("Est. cost", item.estimated_cost or "N/A")
            st.markdown(f"**Why we recommend this:** {item.explanation}")

    if result.meta:
        st.caption(
            f"Considered {result.meta.candidates_considered} restaurants · "
            f"{result.meta.latency_ms} ms"
        )


def main() -> None:
    _configure_utf8_stdio()
    setup_logging()
    st.set_page_config(
        page_title="Zomato AI Recommendations",
        page_icon="🍽️",
        layout="wide",
    )

    st.title("AI Restaurant Recommendations")
    st.caption("Powered by Zomato dataset + Groq LLM")

    try:
        repository = _cached_repository()
    except Exception as exc:
        st.error("Could not load restaurant data. Check your connection and try again.")
        st.caption(str(exc))
        return

    locations = repository.get_locations()
    if not locations:
        st.error("No restaurant locations available in the dataset.")
        return

    with st.sidebar:
        st.header("Your preferences")
        location = st.selectbox(
            "Location",
            locations,
            index=_location_index(locations),
            help="Dataset uses Bangalore area names (e.g. BTM), not city names like Chennai.",
        )
        budget_label = st.selectbox("Budget", list(BUDGET_OPTIONS.keys()), index=1)
        cuisine = st.text_input("Cuisine (optional)", placeholder="e.g. Italian, North Indian")
        min_rating = st.slider("Minimum rating", 0.0, 5.0, 3.5, 0.5)
        additional_text = st.text_area(
            "Additional preferences (optional)",
            placeholder="family-friendly, quick service",
            help="Comma or line separated tags passed to the AI",
        )
        max_results = st.slider("Max results", 1, 10, 5)
        submit = st.button("Get recommendations", type="primary", use_container_width=True)

    if "last_result" not in st.session_state:
        st.session_state.last_result = None
    if "last_error" not in st.session_state:
        st.session_state.last_error = None
    if "last_prefs" not in st.session_state:
        st.session_state.last_prefs = None

    if submit:
        st.session_state.last_error = None
        st.session_state.last_result = None
        prefs = build_preferences_from_form(
            location=location,
            budget_label=budget_label,
            cuisine=cuisine,
            min_rating=min_rating,
            additional_text=additional_text,
            max_results=max_results,
        )
        st.session_state.last_prefs = prefs

        with st.spinner("Finding the best restaurants for you..."):
            try:
                st.session_state.last_result = recommend(prefs)
            except ValueError as exc:
                logger.warning("Validation or API error: %s", exc)
                st.session_state.last_error = str(exc)
            except Exception as exc:
                logger.exception("Recommendation pipeline failed")
                st.session_state.last_error = (
                    f"Recommendation failed: {exc}. "
                    "Check GROQ_API_KEY in .env and try again."
                )

    if st.session_state.last_error:
        st.error(st.session_state.last_error)
        if st.button("Retry"):
            st.session_state.last_error = None
            if st.session_state.last_prefs:
                with st.spinner("Retrying..."):
                    try:
                        st.session_state.last_result = recommend(st.session_state.last_prefs)
                    except Exception as exc:
                        logger.exception("Retry failed")
                        st.session_state.last_error = f"Retry failed: {exc}"
            st.rerun()

    result = st.session_state.last_result
    if result is None and not st.session_state.last_error:
        st.info(
            "Select your preferences in the sidebar and click **Get recommendations**.\n\n"
            "**Demo:** Location `BTM`, Budget `Medium`, Cuisine `North Indian`, Rating ≥ 4.0"
        )
        return

    if isinstance(result, EmptyResult):
        render_empty_state(result)
    elif isinstance(result, RecommendationResponse):
        render_recommendations(result)


if __name__ == "__main__":
    main()
