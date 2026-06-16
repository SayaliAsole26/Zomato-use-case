# Demo Scenarios (Phase 7.7)

Manual verification scripts for the Zomato AI recommendation MVP. Run after setup in [README](../README.md).

## Prerequisites

- `pip install -r requirements.txt`
- `.env` with valid `GROQ_API_KEY`
- Dataset cache at `data/cache/restaurants.parquet` (created on first run)

## Scenario 1 — Happy path (R6)

**Preferences**

| Field | Value |
|-------|--------|
| Location | `BTM` |
| Budget | `medium` |
| Cuisine | `North Indian` |
| Min rating | `4.0` |

**Expected**

- 1–3 recommendations with name, cuisine, rating, cost, AI explanation
- Optional summary paragraph
- `meta.candidates_considered` ≤ 30, `meta.fallback` = false

**CLI**

```bash
python -m src.cli --location BTM --budget medium --cuisine "North Indian" --min-rating 4.0 --max-results 3
```

**Streamlit:** same values in sidebar → **Get recommendations**

---

## Scenario 2 — Empty filters (R3 short-circuit)

**Preferences**

| Field | Value |
|-------|--------|
| Location | `BTM` |
| Budget | `low` |
| Min rating | `5.0` |

**Expected**

- `EmptyResult` message with suggestions
- No Groq API call (check logs: `skipping LLM`)

**Note:** The dataset uses **Bangalore area names** (BTM, Banashankari), not cities like Chennai. Chennai is not in the Streamlit dropdown.

**CLI**

```bash
python -m src.cli --location BTM --budget low --min-rating 5.0
```

---

## Scenario 3 — Strict rating + budget

**Preferences**

| Field | Value |
|-------|--------|
| Location | `Banashankari` |
| Budget | `high` |
| Min rating | `4.5` |

**Expected**

- Either a small set of high-tier matches or empty state
- If matches exist: sorted by rating; LLM ranks among filtered candidates only

**CLI**

```bash
python -m src.cli --location Banashankari --budget high --min-rating 4.5
```

---

## Automated demo runner

Runs scenarios 1 and 2 with mocked LLM (no API cost) plus optional live call:

```bash
python scripts/run_demos.py
python scripts/run_demos.py --live
```

## Requirements traceability

| Req | Verified by |
|-----|-------------|
| R1 | `python scripts/smoke_data.py` |
| R2 | Streamlit form / CLI args |
| R3 | Scenario 2 logs + empty result |
| R4–R5 | Scenario 1 LLM explanations |
| R6 | Scenario 1 output fields |
