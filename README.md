# Zomato AI Restaurant Recommendation

AI-powered restaurant recommendations combining the Hugging Face Zomato dataset with Groq LLM ranking and explanations.

## Requirements (R1–R6)

| # | Requirement | Status |
|---|-------------|--------|
| R1 | Hugging Face dataset loaded and preprocessed | Done |
| R2 | User specifies location, budget, cuisine, min rating, extras | Done |
| R3 | Filtering narrows candidates before LLM | Done |
| R4 | Prompt supports reasoning and ranking | Done |
| R5 | LLM returns ranked recommendations with explanations | Done |
| R6 | UI shows name, cuisine, rating, cost, AI explanation | Done |

## Documentation

- [Project context](docs/context.md)
- [Architecture](docs/architecture.md)
- [Implementation plan](docs/implementation-plan.md)
- [Edge cases](docs/edge-cases.md)
- [Data schema](docs/data-schema.md)
- [Demo scenarios](docs/demo-scenarios.md)

## Prerequisites

- Python 3.11+
- Node.js 18+ (for CulinaAI React frontend)
- Groq API key ([console.groq.com/keys](https://console.groq.com/keys))
- ~600 MB disk for dataset cache (first run)

## Quick start (< 30 min)

```bash
git clone <repo-url>
cd GITHUB
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
copy .env.example .env          # Windows
# cp .env.example .env          # macOS/Linux
```

Edit `.env` and set:

```env
GROQ_API_KEY=gsk_your_key_here
```

Run unit tests (no API key needed):

```bash
python -m pytest
```

Launch the **CulinaAI** React frontend (dev — hot reload):

```bash
# Terminal 1: API backend
uvicorn src.api.main:app --reload --port 8000

# Terminal 2: Vite dev server (proxies /api to :8000)
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** (dev) or build for production:

```bash
cd frontend && npm run build
uvicorn src.api.main:app --port 8000
```

Then open **http://localhost:8000** (serves `frontend/dist` SPA).

Demo: Location `BTM`, Budget `Medium`, Cuisine `North Indian`, Min rating `4.0` → **Find Restaurants**.

Legacy Streamlit UI (optional — not installed in production):

```bash
pip install -r requirements-dev.txt
streamlit run src/app/main.py
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | Groq API key (required for LLM) |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Groq model |
| `HF_DATASET_NAME` | `ManikaSaini/zomato-restaurant-recommendation` | Dataset |
| `MAX_CANDIDATES_FOR_LLM` | `30` | Filter cap before LLM |
| `MAX_RESULTS` | `5` | Default recommendations count |
| `COST_TIER_LOW_MAX` | `500` | INR tier boundary |
| `COST_TIER_MEDIUM_MAX` | `1000` | INR tier boundary |

See [.env.example](.env.example).

## Commands

| Task | Command |
|------|---------|
| Unit tests | `python -m pytest` |
| Live Groq tests | `python -m pytest -m integration` |
| Load data smoke | `python scripts/smoke_data.py` |
| Full pipeline smoke | `python scripts/smoke_recommend.py` |
| CLI recommend | `python -m src.cli --location BTM --budget medium --min-rating 3.5` |
| Demo scenarios | `python scripts/run_demos.py` |
| CulinaAI React UI (dev) | `cd frontend && npm run dev` |
| CulinaAI production build | `cd frontend && npm run build` |
| API backend | `uvicorn src.api.main:app --reload --port 8000` |
| Check `.env` | `python scripts/check_env.py` |

## UI stack

**CulinaAI** — **React 19 + Vite + TypeScript + Tailwind** frontend implementing the Google Stitch design. Design tokens in [design/stitch_zomato_ai_palettestraight/gourmet_intelligence/DESIGN.md](design/stitch_zomato_ai_palettestraight/gourmet_intelligence/DESIGN.md).

- Dev: Vite on `:5173` with API proxy to FastAPI `:8000`
- Prod: `npm run build` → FastAPI serves `frontend/dist` as SPA

**Streamlit** — legacy MVP UI in `src/app/main.py`.

## Project layout

```text
frontend/               # CulinaAI React + Vite + Tailwind
  src/
    pages/              # Home, Discover
    components/         # Cards, sidebar, layout
    api/client.ts       # FastAPI client
  package.json
src/
  app/main.py           # Streamlit UI (legacy)
  api/main.py           # FastAPI API + serves frontend/dist
  cli.py                # CLI entry
  orchestrator.py       # recommend() pipeline
  config/settings.py    # Environment config
  data/                 # Loader, preprocessor, repository
  integration/          # Filter, prompt, parser
  llm/client.py         # Groq adapter
  models/               # Pydantic models
tests/                  # pytest suite
scripts/                # Smoke & demo scripts
docs/                   # Architecture & plans
data/cache/             # Preprocessed parquet (gitignored)
```

## REST API (Phase 8)

Start the server (also serves the CulinaAI frontend):

```bash
uvicorn src.api.main:app --reload --port 8000
```

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Production SPA (after `npm run build`) |
| http://localhost:5173 | Vite dev server (with `npm run dev`) |
| http://localhost:8000/discover | Discover route (production) |
| http://localhost:8000/docs | OpenAPI Swagger |

**Health check:**

```bash
curl http://localhost:8000/health
```

**Recommendations (same preferences as the UI demo):**

```bash
curl -X POST http://localhost:8000/api/v1/recommendations ^
  -H "Content-Type: application/json" ^
  -d "{\"location\":\"BTM\",\"budget\":\"medium\",\"cuisine\":\"North Indian\",\"min_rating\":4.0,\"max_results\":5}"
```

On macOS/Linux, use `\` line continuations and single quotes for the JSON body.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Dataset loaded flag and record count |
| `/api/v1/recommendations` | POST | Run recommendation pipeline |
| `/docs` | GET | Swagger UI (auto-generated) |

Validation errors return **422**. No matching restaurants return **200** with an empty `recommendations` array plus `message` and `suggestions`.

## Logging

Structured logs include `dataset.load.*`, `filter.input_count`, `recommendation.request_id`, and LLM latency in meta. API keys are never logged.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 401 from Groq | Regenerate key at console.groq.com/keys |
| Empty results | Try area names from dropdown (e.g. `BTM`, `Banashankari`) |
| Slow first start | Dataset loads once; cached in `data/cache/` |
| Unicode in CLI (Windows) | CLI reconfigures stdout to UTF-8 |
| Port 8501 already in use | Stop other Streamlit: `Get-Process streamlit | Stop-Process` then restart |
| Port 8000 already in use | Use `uvicorn src.api.main:app --port 8001` or stop the other process |

## License

Academic / demo project for Zomato use case.
