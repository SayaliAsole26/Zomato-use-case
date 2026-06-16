# CulinaAI – Frontend Documentation

## Overview
CulinaAI is an AI-powered restaurant discovery platform inspired by Zomato. The UI supports:
- Restaurant recommendations
- AI-generated explanations
- Search and filtering
- Empty-state guidance
- Saved restaurants (browser-only, no account)
- Responsive desktop and mobile experiences

**v1 scope:** No sign-in, registration, or user accounts. Saved restaurants persist in the browser via local storage only.

## Tech Stack (implemented)
- React 19 + Vite + TypeScript
- Tailwind CSS
- Zustand (search preferences + local favorites)
- Axios
- React Query
- React Router

## Pages

### 1. Home Page
Features:
- Hero and product overview
- Popular restaurants (Trending, Highly Rated, New Opening)
- CTA to Search

### 2. Search Page
Features:
- Search bar
- Cuisine filters
- Budget filters
- Rating filters
- Location selector
- AI recommendation cards

### 3. Recommendation Results
Restaurant card includes:
- Hero image
- Restaurant name
- Cuisine tags
- Rating badge
- AI reasoning panel
- Match percentage
- Share button
- Save/Favorite button (local storage)

### 4. No Results State
Displays:
- Friendly empty state illustration
- AI insight explaining why no matches exist
- Suggested actions:
  - Change location
  - Adjust budget
  - Remove cuisine filters

### 5. Popular Restaurants Section
Cards:
- Trending
- New Opening
- Highly Rated

### 6. Saved Page
Features:
- List of restaurants saved from search results
- Stored in browser localStorage (Zustand persist)
- No sign-in required
- Cleared if user clears site data

## Out of scope (v1)
- Sign In / Sign Up
- User profiles
- Server-side search history
- Notifications
- Account settings

These may be added in a future version with backend auth.

## Suggested Folder Structure

```text
src/
├── components/
│   ├── Navbar/
│   ├── SearchBar/
│   ├── Filters/
│   ├── RestaurantCard/
│   ├── RecommendationBadge/
│   ├── AIReasoningCard/
│   ├── EmptyState/
│   └── PopularRestaurants/
├── pages/
│   ├── search/
│   └── saved/
├── hooks/
├── services/
├── store/              # searchStore, favoritesStore (local)
├── layouts/
└── types/
```

## Core Components

### RestaurantCard
Props:
- id
- name
- cuisine
- rating
- image
- aiReason
- matchScore
- saved (optional)
- onSave / onShare (optional)

### AIReasoningCard
Displays:
- Why picked
- AI reasoning
- Best value finding
- Similar preference match

### Filters
Supports:
- Cuisine
- Budget
- Rating
- Location
- Additional preferences (free text)

## Responsive Design

### Mobile
- Single-column cards
- Sticky filters
- Bottom CTA

### Desktop
- Sidebar navigation
- Multi-column layout
- Expanded AI explanations

## State Management

| Store | Purpose |
|-------|---------|
| `searchStore` | User preferences form state |
| `favoritesStore` | Saved restaurants (localStorage persist) |
| React Query | API data: locations, recommendations, popular |

No auth store or server-backed user session in v1.

## API Endpoints Consumed

All requests use `/api/v1` prefix. Production builds set `VITE_API_URL` to the Railway backend URL.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/locations` | GET | Location dropdown options |
| `/api/v1/recommendations` | POST | AI recommendations |
| `/api/v1/restaurants/search` | GET | Filtered restaurant search |
| `/api/v1/restaurants/popular` | GET | Trending / rated / new |
| `/api/v1/restaurants/{id}` | GET | Restaurant detail |
| `/health` | GET | Backend health (optional) |

**Not used in v1:** `/auth/*`, `/favorites`, `/history`

## Deployment
- **Frontend:** Vercel (`frontend/` root, `vercel.json` SPA rewrites)
- **Backend:** Railway (separate service)
- See [docs/deployment-plan.md](../docs/deployment-plan.md)

## UX Enhancements
- Skeleton loaders
- Lazy image loading
- AI explanation tooltips
- Dark mode support (future)

## Future Enhancements
- User accounts and sign-in
- Server-synced favorites and search history
- Infinite scrolling
- Notifications
