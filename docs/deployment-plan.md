# CulinaAI Deployment Plan

Deploy the **FastAPI backend on Railway** and the **React (Vite) frontend on Vercel**. The frontend calls the backend over HTTPS; there is no sign-in or user database in this version.

## Architecture

```text
User browser
    │
    ▼
Vercel (static SPA)          Railway (FastAPI + uvicorn)
https://your-app.vercel.app   https://your-api.up.railway.app
    │                                    │
    │  HTTPS  /api/v1/*  /health         │
    └────────────────────────────────────┘
                                         ├── Groq API (LLM)
                                         └── Hugging Face dataset → parquet cache
```

| Component | Platform | Serves |
|-----------|----------|--------|
| Frontend | Vercel | React SPA (`frontend/dist`) |
| Backend | Railway | REST API only (no bundled UI in split deploy) |

---

## Prerequisites

- GitHub repo connected to Railway and Vercel
- [Groq API key](https://console.groq.com/keys)
- Railway account (Hobby or Pro recommended for memory/disk)
- Vercel account

**Local verification before deploy:**

```bash
python -m pytest -m "not integration"
cd frontend && npm run build
```

---

## Part 1 — Backend on Railway

### 1.1 Create the Railway service

1. [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
2. Select this repository
3. **Root directory:** `/` (repo root, not `frontend/`)
4. **Service type:** Web

### 1.2 Build & start commands

Railway auto-detects Python from `requirements.txt`. Set these in **Settings → Deploy**:

| Setting | Value |
|---------|--------|
| **Build command** | `pip install -r requirements.txt` |
| **Start command** | `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT` |

Railway injects `$PORT`; do not hard-code `8000` or `8001`.

Optional **Procfile** at repo root (Railway picks it up automatically):

```text
web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
```

### 1.3 Environment variables (Railway)

In **Variables**, add:

| Variable | Required | Example / notes |
|----------|----------|-----------------|
| `GROQ_API_KEY` | Yes | `gsk_...` |
| `LLM_MODEL` | No | `llama-3.3-70b-versatile` |
| `HF_DATASET_NAME` | No | `ManikaSaini/zomato-restaurant-recommendation` |
| `DATA_CACHE_PATH` | No | `data/cache/restaurants.parquet` |
| `MAX_CANDIDATES_FOR_LLM` | No | `30` |
| `MAX_RESULTS` | No | `5` |
| `COST_TIER_LOW_MAX` | No | `500` |
| `COST_TIER_MEDIUM_MAX` | No | `1000` |

Do **not** commit `.env` to git.

### 1.4 Dataset cache & cold start

On first boot the app downloads and preprocesses the Hugging Face dataset (~600 MB on disk). This can take several minutes.

**Recommendations:**

1. **Persistent volume (recommended):** Railway → service → **Volumes** → mount e.g. `/app/data/cache` and keep `DATA_CACHE_PATH=data/cache/restaurants.parquet`
2. **Plan for slow first request** after deploy or scale-to-zero wake-up
3. Ensure enough **memory** (≥ 1 GB) and **disk** for parquet + pandas

### 1.5 Public URL & health check

1. **Settings → Networking → Generate domain** (e.g. `https://culinaai-api-production.up.railway.app`)
2. Verify:

```bash
curl https://YOUR-RAILWAY-URL.up.railway.app/health
```

Expected:

```json
{"status":"ok","dataset_loaded":true,"restaurant_count":12143}
```

3. Optional: set **Healthcheck path** to `/health` in Railway

### 1.6 CORS

The API already allows all origins in `src/api/main.py`:

```python
allow_origins=["*"]
```

This is required so the Vercel frontend can call Railway from the browser.

### 1.7 API endpoints (production)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health + dataset status |
| `/api/v1/locations` | GET | Location dropdown data |
| `/api/v1/recommendations` | POST | AI recommendations |
| `/api/v1/restaurants/search` | GET | Filtered search |
| `/api/v1/restaurants/popular` | GET | Trending / rated / new |
| `/api/v1/restaurants/{id}` | GET | Restaurant detail |
| `/docs` | GET | Swagger UI |

Auth, favorites, and history endpoints are **not** deployed (removed from this project).

### 1.8 Railway troubleshooting

| Issue | Action |
|-------|--------|
| Build fails on `pyarrow` / pandas | Use Railway Python 3.11+; ensure `requirements.txt` is at repo root |
| OOM on startup | Increase memory; reduce concurrent workers (single uvicorn process is fine) |
| `dataset_loaded: false` | Check logs; confirm HF access and disk space; verify volume mount |
| 401 from Groq | Rotate `GROQ_API_KEY` in Railway variables |
| 429 rate limit | Built-in limiter: 60 req/min/IP on API routes |

---

## Part 2 — Frontend on Vercel

### 2.1 One-time code change (API base URL)

Vite dev uses a proxy; production on Vercel must point at the Railway URL.

Update `frontend/src/services/api.ts`:

```typescript
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "",
  headers: { "Content-Type": "application/json" },
});
```

Add to `frontend/src/vite-env.d.ts`:

```typescript
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
}
```

Commit and push before deploying.

### 2.2 Create the Vercel project

1. [vercel.com](https://vercel.com) → **Add New → Project** → import GitHub repo
2. **Root Directory:** `frontend`
3. **Framework Preset:** Vite
4. **Build Command:** `npm run build`
5. **Output Directory:** `dist`
6. **Install Command:** `npm install`

### 2.3 Environment variables (Vercel)

| Variable | Value |
|----------|--------|
| `VITE_API_URL` | `https://YOUR-RAILWAY-URL.up.railway.app` |

No trailing slash. Redeploy after changing env vars (Vite bakes them in at build time).

### 2.4 SPA routing (React Router)

Create `frontend/vercel.json` so client routes work on refresh:

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

Routes: `/`, `/search`, `/saved` (and `/discover` → redirects to `/search` in-app).

### 2.5 Deploy & verify

1. Deploy from Vercel dashboard or push to the connected branch
2. Open `https://your-app.vercel.app`
3. **Search** page should load locations from Railway
4. Run a recommendation search (requires valid `GROQ_API_KEY` on Railway)

**Browser check (DevTools → Network):** requests should go to  
`https://YOUR-RAILWAY-URL.up.railway.app/api/v1/...`, not to the Vercel domain.

### 2.6 Saved restaurants

Saved items use **localStorage** only (Zustand persist). No backend call; works the same on Vercel without extra setup.

### 2.7 Vercel troubleshooting

| Issue | Action |
|-------|--------|
| “Could not load restaurant dataset” | Wrong or missing `VITE_API_URL`; redeploy after fixing |
| CORS errors | Confirm Railway URL in `VITE_API_URL`; backend CORS is `*` |
| 404 on `/search` refresh | Add `vercel.json` rewrites (§2.4) |
| API works locally, not on Vercel | Rebuild on Vercel after env change |

---

## Part 3 — Deployment order

1. Deploy **backend** on Railway → note public URL → confirm `/health`
2. Apply **frontend API URL** code change (§2.1) if not already done
3. Set **`VITE_API_URL`** on Vercel to the Railway URL
4. Add **`frontend/vercel.json`** (§2.4)
5. Deploy **frontend** on Vercel
6. End-to-end test: Home → Search → Find Restaurants

---

## Part 4 — Optional hardening

| Topic | Suggestion |
|-------|------------|
| Custom domains | Railway + Vercel → add DNS CNAMEs in each dashboard |
| CORS lock-down | Replace `allow_origins=["*"]` with `[os.environ["FRONTEND_URL"]]` |
| Secrets | Never commit keys; use Railway/Vercel env UI only |
| CI | Run `pytest` and `npm run build` on PR before merge |
| Monitoring | Watch Railway logs for dataset load and Groq errors |
| Slim image | Optional prod `requirements-prod.txt` without `streamlit` / `pytest` |

---

## Part 5 — Quick reference

```bash
# Railway (local smoke against deployed API)
curl https://YOUR-RAILWAY-URL.up.railway.app/health

curl -X POST https://YOUR-RAILWAY-URL.up.railway.app/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{"location":"BTM","budget":"medium","cuisine":"North Indian","min_rating":4.0,"max_results":5}'

# Vercel CLI (optional)
cd frontend
vercel --prod
```

| Environment | Frontend | Backend |
|-------------|----------|---------|
| Local dev | http://127.0.0.1:5173 | http://127.0.0.1:8001 |
| Production | `https://*.vercel.app` | `https://*.up.railway.app` |

---

## Related docs

- [README.md](../README.md) — local setup
- [architecture.md](./architecture.md) — system design
- [implementation-plan.md](./implementation-plan.md) — feature phases
- [context.md](./context.md) — scope (no auth in v1)
