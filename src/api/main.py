"""FastAPI application exposing the recommendation orchestrator (Phase 8)."""

from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Callable

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.api.deps import get_llm_client_dep, get_repository_dep, get_settings_dep
from src.api.routers import restaurants_router
from src.api.schemas import HealthResponse, LocationsResponse, RecommendationApiResponse
from src.config.settings import Settings
from src.data.repository import RestaurantRepository
from src.llm.client import LLMClient
from src.logging_config import setup_logging
from src.models.preferences import UserPreferences
from src.models.recommendation import EmptyResult, RecommendationMeta, RecommendationResponse
from src.orchestrator import recommend

logger = logging.getLogger(__name__)

API_PREFIX = "/api/v1"
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
FRONTEND_DIST = FRONTEND_DIR / "dist"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter (Phase 8.5)."""

    def __init__(
        self,
        app,
        *,
        max_requests: int = 60,
        window_seconds: int = 60,
    ) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path
        if (
            path.startswith("/health")
            or path.startswith("/assets")
            or path.startswith("/openapi")
            or path in ("/", "/discover", "/search", "/saved")
        ):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window = self._hits[client_ip]

        while window and now - window[0] > self.window_seconds:
            window.popleft()

        if len(window) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
            )

        window.append(now)
        return await call_next(request)


@asynccontextmanager
async def _lifespan(app: FastAPI):
    setup_logging()
    yield


def create_app(
    *,
    settings: Settings | None = None,
    enable_rate_limit: bool = True,
    mount_frontend: bool = True,
) -> FastAPI:
    """Application factory for production and tests."""
    app = FastAPI(
        title="CulinaAI Restaurant Recommendations",
        description="REST API and CulinaAI web UI for personalized restaurant recommendations",
        version="1.0.0",
        lifespan=_lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if enable_rate_limit:
        app.add_middleware(RateLimitMiddleware)

    app.include_router(restaurants_router.router, prefix=API_PREFIX)

    def _resolve_settings() -> Settings:
        return settings or get_settings_dep()

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    def health(repo: RestaurantRepository = Depends(get_repository_dep)) -> HealthResponse:
        try:
            count = repo.count()
            loaded = count > 0
        except Exception as exc:
            logger.error("health check failed: %s", exc)
            loaded = False
            count = 0

        return HealthResponse(
            status="ok" if loaded else "degraded",
            dataset_loaded=loaded,
            restaurant_count=count,
        )

    @app.get(
        f"{API_PREFIX}/locations",
        response_model=LocationsResponse,
        tags=["recommendations"],
    )
    def list_locations(repo: RestaurantRepository = Depends(get_repository_dep)) -> LocationsResponse:
        return LocationsResponse(locations=repo.get_locations())

    @app.post(
        f"{API_PREFIX}/recommendations",
        response_model=RecommendationApiResponse,
        tags=["recommendations"],
    )
    def create_recommendations(
        prefs: UserPreferences,
        repo: RestaurantRepository = Depends(get_repository_dep),
        llm_client: LLMClient = Depends(get_llm_client_dep),
        cfg: Settings = Depends(_resolve_settings),
    ) -> RecommendationApiResponse:
        try:
            result = recommend(
                prefs,
                repository=repo,
                llm_client=llm_client,
                settings=cfg,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except Exception as exc:
            logger.exception("recommendation request failed")
            raise HTTPException(status_code=500, detail="Recommendation pipeline failed") from exc

        return _to_api_response(result)

    if mount_frontend and FRONTEND_DIST.is_dir():
        assets_dir = FRONTEND_DIST / "assets"
        if assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

        index_file = FRONTEND_DIST / "index.html"

        @app.get("/", include_in_schema=False)
        def serve_spa_root() -> FileResponse:
            return FileResponse(index_file)

        @app.get("/discover", include_in_schema=False)
        def serve_spa_discover() -> FileResponse:
            return FileResponse(index_file)

        @app.get("/search", include_in_schema=False)
        def serve_spa_search() -> FileResponse:
            return FileResponse(index_file)

        @app.get("/saved", include_in_schema=False)
        def serve_spa_saved() -> FileResponse:
            return FileResponse(index_file)

    return app


def _to_api_response(result: RecommendationResponse | EmptyResult) -> RecommendationApiResponse:
    if isinstance(result, EmptyResult):
        return RecommendationApiResponse(
            recommendations=[],
            message=result.message,
            suggestions=result.suggestions,
            meta=RecommendationMeta(
                candidates_considered=0,
                latency_ms=0,
                fallback=False,
            ),
        )

    return RecommendationApiResponse(
        summary=result.summary,
        recommendations=result.recommendations,
        meta=result.meta,
    )


app = create_app()
