# CulinaAI – Backend Documentation

## Overview
Backend powers:
- Restaurant search and listing
- AI recommendations with explanations
- Location and popular-restaurant data
- Health and dataset readiness checks

**v1 scope:** No authentication, user profiles, server-side favorites, or search history. The frontend saves favorites in browser local storage only.

## Implemented Stack
- Python 3.11+ / FastAPI
- Uvicorn
- Groq LLM (Llama 3.3)
- Hugging Face Zomato dataset → local parquet cache
- In-memory restaurant repository
- Rate limiting (in-memory middleware)

## Recommended Stack (future / scale)
- PostgreSQL
- Redis Cache
- Vector Database (Pinecone / Weaviate)
- Docker

## High-Level Architecture (v1)

```text
User → Vercel (React SPA) → Railway (FastAPI) → Groq API
                                      ↓
                            Parquet cache (HF dataset)
```

AI Flow (implemented):
```text
User Preferences
→ Filter candidates (location, budget, cuisine, rating)
→ Empty? → structured empty response
→ Build prompt → Groq LLM → Parse JSON → Ranked recommendations
```

## Services (implemented)

### Health Service
- `GET /health` — dataset loaded flag and restaurant count

### Restaurant Service
Prefix: `/api/v1/restaurants`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/restaurants` | GET | Paginated list |
| `/api/v1/restaurants/search` | GET | Filter by location, cuisine, budget, rating |
| `/api/v1/restaurants/popular` | GET | Trending, highly rated, new opening |
| `/api/v1/restaurants/{id}` | GET | Single restaurant detail |

Responsibilities:
- Restaurant retrieval from preprocessed dataset
- Filtering, sorting, pagination
- Match score (weighted ranking formula)

### Recommendation Service
- `GET /api/v1/locations` — unique locations for UI dropdowns
- `POST /api/v1/recommendations` — full LLM recommendation pipeline

Input:
```json
{
  "location": "BTM",
  "budget": "medium",
  "cuisine": "North Indian",
  "min_rating": 4.0,
  "max_results": 5,
  "additional": ["family-friendly"]
}
```

Output:
```json
{
  "summary": "Top picks in BTM",
  "recommendations": [
    {
      "restaurant_id": "…",
      "name": "…",
      "cuisine": "…",
      "rating": 4.5,
      "estimated_cost": "₹800 for two",
      "explanation": "…",
      "rank": 1
    }
  ],
  "meta": {
    "candidates_considered": 12,
    "latency_ms": 1200,
    "fallback": false
  }
}
```

Empty filter result (200):
```json
{
  "recommendations": [],
  "message": "No restaurants match your preferences.",
  "suggestions": ["Try a different location", "…"],
  "meta": { "candidates_considered": 0, "latency_ms": 0, "fallback": false }
}
```

## Removed from v1 (previously designed, not shipped)

The following were removed to keep the product sign-in-free:

| Feature | Former endpoints | Replacement |
|---------|------------------|-------------|
| Authentication | `POST /auth/register`, `/auth/login`, `/auth/logout` | None |
| Server favorites | `POST/GET/DELETE /favorites` | Frontend localStorage |
| Search history | `GET/POST /history` | None |

## Data Layer (implemented)

Restaurant records are loaded from:
- **Source:** `ManikaSaini/zomato-restaurant-recommendation` (Hugging Face)
- **Cache:** `data/cache/restaurants.parquet` (~12k records)
- **Repository:** in-memory read-only store with filter/query helpers

No PostgreSQL or user tables in v1.

### Restaurant record (canonical)
| Field | Type |
|-------|------|
| id | string |
| name | string |
| location | string |
| cuisines | list[string] |
| rating | float |
| cost_for_two | int |
| cost_tier | low / medium / high |
| votes | int |

## AI Recommendation Engine

### Inputs (v1)
- Cuisine preference
- Budget tier
- Location
- Rating threshold
- Additional free-text preferences

### Inputs (future)
- User history
- Saved restaurants (server-side)

### Ranking Formula (search / match score)

Final Score =
0.35 × Cuisine Match +
0.25 × Rating Score +
0.20 × Budget Match +
0.10 × Distance Score +
0.10 × User Behavior Score

*(Distance and behavior use defaults when geo/user data is unavailable.)*

## Vector Search (future)

Restaurant metadata converted into embeddings for similarity search. Not implemented in v1; filtering uses rule-based candidate selection before LLM ranking.

## Caching (implemented)

- Parquet file cache for preprocessed dataset
- Singleton repository (`lru_cache`) after first load

Future: Redis for popular restaurants and search results.

## Security (v1)

- Rate limiting (60 req/min/IP on API routes)
- HTTPS (via Railway / Vercel)
- Pydantic input validation
- CORS enabled for cross-origin frontend (Vercel → Railway)
- API keys via environment variables (`GROQ_API_KEY`); never logged

**Not in v1:** JWT authentication, password hashing, user sessions

## Deployment (implemented)

| Component | Platform |
|-----------|----------|
| Backend | Railway — `Procfile`: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT` |
| Frontend | Vercel — separate SPA, `VITE_API_URL` points to Railway |

See [docs/deployment-plan.md](../docs/deployment-plan.md).

Environment variables:
| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq LLM API key |
| `LLM_MODEL` | No | Default `llama-3.3-70b-versatile` |
| `HF_DATASET_NAME` | No | Hugging Face dataset id |
| `DATA_CACHE_PATH` | No | Parquet cache path |
| `MAX_CANDIDATES_FOR_LLM` | No | Filter cap before LLM |
| `MAX_RESULTS` | No | Default recommendation count |

## Monitoring (future)
- Prometheus
- Grafana
- Sentry

## Future Enhancements
- User accounts, JWT auth, server-side favorites and history
- PostgreSQL + Redis
- Vector search and personalized learning
- Table booking integration
- Real-time availability
- Multi-city support
- Voice-based restaurant search
