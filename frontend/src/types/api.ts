export type Budget = "low" | "medium" | "high";

export interface UserPreferences {
  location: string;
  budget: Budget;
  cuisine?: string | null;
  min_rating?: number | null;
  additional?: string[];
  max_results?: number;
}

export interface RecommendationItem {
  restaurant_id: string;
  name: string;
  cuisine: string;
  rating: number | null;
  estimated_cost: string | null;
  explanation: string;
  rank: number;
}

export interface RecommendationMeta {
  candidates_considered: number;
  latency_ms: number | null;
  fallback: boolean;
}

export interface RecommendationApiResponse {
  summary: string | null;
  recommendations: RecommendationItem[];
  meta: RecommendationMeta | null;
  message: string | null;
  suggestions: string[] | null;
}

export interface RestaurantSummary {
  id: string;
  name: string;
  cuisine: string;
  location: string;
  rating: number | null;
  price_range: string | null;
  estimated_cost: string | null;
  votes: number | null;
  address: string | null;
  match_score: number | null;
}

export interface RestaurantListResponse {
  restaurants: RestaurantSummary[];
  total: number;
  limit: number;
  offset: number;
}

export interface PopularRestaurantsResponse {
  trending: RestaurantSummary[];
  highly_rated: RestaurantSummary[];
  new_opening: RestaurantSummary[];
}

export interface PreferencesFormState {
  location: string;
  budget: Budget;
  cuisine: string;
  minRating: number;
  maxResults: number;
  additional: string;
}

export interface LocationsResponse {
  locations: string[];
}
