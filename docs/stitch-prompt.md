# Google Stitch Design Prompt

**Project name:** Zomato AI Restaurant Recommendations  
**Product type:** Web app (desktop-first, responsive mobile)  
**Design goal:** Redesign a functional but basic MVP into a polished, modern food-discovery experience that feels trustworthy, smart, and easy to use — inspired by Zomato’s clarity, with a distinct AI-first identity.

---

## Product overview

Build UI designs for an **AI-powered restaurant recommendation app** that helps users find the best places to eat based on personal preferences.

The system works in two stages:

1. **Deterministic filtering** over a real restaurant dataset (location, budget, cuisine, rating).
2. **LLM ranking + explanation** — AI ranks matches and explains *why* each restaurant fits the user.

**Tagline direction:** “Smart picks, explained for you” / “Your AI food guide for Bangalore”

**Brand tone:** Friendly, confident, food-forward, not gimmicky. The AI should feel helpful and transparent, not like a black box.

**Important data note:** Locations are **Bangalore area names** (e.g. BTM, Banashankari, Indiranagar), not full city names. The UI should guide users with helper text like “Select a neighborhood in Bangalore.”

---

## Target users

- Students and professionals looking for dinner options in a specific area
- Demo/evaluator audience (professors, reviewers) who need to understand the AI value quickly
- No login or accounts in v1 — single-session use

---

## Screens to design (minimum)

Design **one cohesive flow** with these states:

### 1. Landing / Home (before search)

- Hero section explaining the product in one sentence
- Primary CTA: “Find restaurants”
- Optional: small “How it works” 3-step strip: **Set preferences → AI filters & ranks → Get explained picks**
- Subtle trust cues: “Powered by real Zomato dataset + AI”

### 2. Preferences panel (main input)

Collect these fields:

| Field | Control type | Notes |
|-------|--------------|-------|
| **Location** | Searchable dropdown | ~93 Bangalore areas; default `BTM` |
| **Budget** | Segmented control | Low / Medium / High (₹ tiers) |
| **Cuisine** | Text input with chips/suggestions | Optional, e.g. “North Indian”, “Italian” |
| **Minimum rating** | Slider | 0–5, step 0.5; default ~3.5 |
| **Additional preferences** | Multi-line text or tag input | e.g. “family-friendly, quick service” |
| **Max results** | Stepper or slider | 1–10, default 5 |

**Primary button:** “Get recommendations” (full width on mobile)

**Secondary:** “Reset filters”

Include inline validation hints (e.g. location required).

### 3. Loading state

Two-phase loading if possible:

- “Loading restaurant dataset…” (first visit)
- “Finding the best matches for you…” (AI thinking)

Use skeleton cards for results area, not just a spinner.

### 4. Results — Success state

**Optional AI summary** at top (1–2 sentences), e.g.  
*“Top North Indian picks in BTM within your medium budget and 4.0+ rating.”*

**Recommendation cards** (ranked #1, #2, #3…), each showing:

- **Rank badge** (#1, #2, #3)
- **Restaurant name** (headline)
- **Cuisine** (tags/chips)
- **Rating** (star + number, e.g. 4.5/5)
- **Estimated cost** (e.g. “₹800 for two”)
- **AI explanation** block — visually distinct (“Why we recommend this”) with 2–3 lines of natural language
- Optional: subtle “View on map” placeholder (non-functional in v1 is fine)

**Footer meta line:**  
“Considered 12 restaurants · 2.4s” (small, muted)

### 5. Empty state (no matches)

Friendly empty illustration + message:  
*“No restaurants match your preferences. Try broadening your filters.”*

Actionable suggestions as clickable chips:

- Try a different location
- Adjust budget
- Remove cuisine filter
- Lower minimum rating

No harsh error styling — this is expected behavior.

### 6. Error / fallback states

- **API/LLM error:** Banner with retry button; show actual error message area
- **Fallback mode:** Info banner — “Showing top-rated matches (AI unavailable)”
- **Dataset load failure:** Clear error with retry

---

## Layout direction

**Desktop (1280px+):**

- Left sidebar or sticky left panel: preference form (~320–380px)
- Right main area: results, summary, cards in a vertical list
- Max content width ~1200px, centered

**Mobile:**

- Collapsible “Filters” drawer or top accordion
- Full-width recommendation cards
- Sticky bottom CTA for “Get recommendations”

---

## Visual style direction

**Aesthetic:** Modern food-tech, clean, premium but approachable — think Zomato meets Notion meets a light AI product.

**Color palette (suggested):**

- Primary: warm red/coral (food appetite, Zomato-adjacent but not identical)
- Secondary: deep green or teal (trust, “recommended”)
- Accent: soft amber for ratings
- Neutrals: warm gray background (#F8F7F5), white cards, dark text (#1A1A1A)

**Typography:**

- Headings: bold, friendly sans (e.g. Inter, Plus Jakarta Sans)
- Body: readable 16px, line-height 1.5
- AI explanation: slightly different treatment (italic or left accent bar) to separate from structured data

**Components:**

- Rounded cards (12–16px radius), soft shadow
- Star ratings, budget pills (Low/Medium/High with ₹ hints)
- Cuisine chips
- Rank badges with gradient or gold accent for #1

**Imagery:**

- Use food/restaurant placeholder photos on cards (optional but recommended)
- Empty state: simple illustration (plate + magnifying glass)

**Do NOT include:** login, signup, payment, booking, cart, maps integration, user profile — out of scope for v1.

---

## Sample content for realistic mockups

Use this demo scenario in the designs:

**User input:**

- Location: BTM
- Budget: Medium
- Cuisine: North Indian
- Min rating: 4.0
- Max results: 3

**Sample results:**

**#1 Pin Me Down**  
Cuisine: Continental, Mexican, Chinese, North Indian · ⭐ 4.5 · ₹800 for two  
*Why:* Best match for BTM, medium budget, North Indian options, and strong 4.5 rating.

**#2 The Biryani Story**  
Cuisine: Biryani, North Indian, Chinese, Mughlai · ⭐ 4.4 · ₹600 for two  
*Why:* Excellent biryani-focused spot within budget with high ratings.

**#3 Cucumber Town**  
Cuisine: Kerala, North Indian · ⭐ 4.2 · ₹600 for two  
*Why:* Solid North Indian choice that meets your minimum rating.

**Summary:**  
*“Top 3 North Indian-friendly restaurants in BTM within your medium budget and 4.0+ rating.”*

---

## UX principles to follow

1. **Filter before AI** — show that results are grounded in real data, not hallucinated
2. **Explainability first** — the AI “why” is the hero, not hidden
3. **Progressive disclosure** — keep advanced fields (additional prefs, max results) collapsible
4. **Graceful degradation** — empty and error states feel helpful, not broken
5. **Speed perception** — skeleton loaders, clear progress during AI wait
6. **Accessibility** — WCAG-friendly contrast, focus states, readable touch targets (44px min)

---

## Deliverables requested from Stitch

1. **Desktop:** Home + Preferences + Results (success)
2. **Desktop:** Empty state + Error/fallback state
3. **Mobile:** Results view + Filters drawer
4. **Component sheet:** buttons, inputs, cards, badges, sliders, chips, banners
5. **Design tokens:** colors, typography scale, spacing, border radius, shadows

---

## Technical context (for implementation handoff)

- Backend API exists: `POST /api/v1/recommendations` with JSON request/response
- Frontend will likely be rebuilt in **React** (or enhanced Streamlit) — design for component reuse
- Currency: **INR (₹)**
- Rating scale: **0–5 stars**
- Default recommendations: **5** (user can set 1–10)

**API request shape:**

```json
{
  "location": "BTM",
  "budget": "medium",
  "cuisine": "North Indian",
  "min_rating": 4.0,
  "additional": ["family-friendly"],
  "max_results": 5
}
```

**API response shape:**

```json
{
  "summary": "Top picks in BTM for your preferences.",
  "recommendations": [
    {
      "restaurant_id": "string",
      "name": "Pin Me Down",
      "cuisine": "north indian, continental",
      "rating": 4.5,
      "estimated_cost": "₹800 for two",
      "explanation": "Best match for your budget and cuisine.",
      "rank": 1
    }
  ],
  "meta": {
    "candidates_considered": 12,
    "latency_ms": 2400,
    "fallback": false
  }
}
```

---

## What to avoid

- Cluttered dashboard aesthetics
- Overly “chatbot” UI (this is form → results, not a chat thread)
- Dark-only theme (light mode primary; dark mode optional)
- Copying Zomato branding/logo directly — inspired, not identical

---

## Source documents

- [Project context](./context.md)
- [Architecture](./architecture.md)

---

**End prompt.** Paste the sections above into Google Stitch to generate high-fidelity, production-ready UI mockups suitable for developer handoff.
