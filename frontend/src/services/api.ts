import axios from "axios";
import type {
  LocationsResponse,
  PopularRestaurantsResponse,
  RecommendationApiResponse,
  RestaurantListResponse,
  RestaurantSummary,
  UserPreferences,
} from "../types/api";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "",
  headers: { "Content-Type": "application/json" },
});

function extractError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    return error.message;
  }
  return error instanceof Error ? error.message : "Request failed";
}

export async function fetchLocations(): Promise<string[]> {
  const { data } = await api.get<LocationsResponse>("/api/v1/locations");
  return data.locations;
}

export async function fetchRecommendations(
  preferences: UserPreferences,
): Promise<RecommendationApiResponse> {
  try {
    const { data } = await api.post<RecommendationApiResponse>(
      "/api/v1/recommendations",
      preferences,
    );
    return data;
  } catch (error) {
    throw new Error(extractError(error));
  }
}

export async function searchRestaurants(params: {
  location?: string;
  cuisine?: string;
  budget?: string;
  min_rating?: number;
  limit?: number;
}): Promise<RestaurantListResponse> {
  const { data } = await api.get<RestaurantListResponse>("/api/v1/restaurants/search", {
    params,
  });
  return data;
}

export async function fetchPopularRestaurants(
  location?: string,
): Promise<PopularRestaurantsResponse> {
  const { data } = await api.get<PopularRestaurantsResponse>("/api/v1/restaurants/popular", {
    params: location ? { location } : undefined,
  });
  return data;
}

export async function fetchRestaurant(id: string): Promise<RestaurantSummary> {
  const { data } = await api.get<RestaurantSummary>(`/api/v1/restaurants/${id}`);
  return data;
}

export function toApiPreferences(form: {
  location: string;
  budget: UserPreferences["budget"];
  cuisine: string;
  minRating: number;
  maxResults: number;
  additional: string;
}): UserPreferences {
  const additional = form.additional
    .split(/[,\n]/)
    .map((t) => t.trim())
    .filter(Boolean);

  return {
    location: form.location,
    budget: form.budget,
    cuisine: form.cuisine.trim() || null,
    min_rating: form.minRating > 0 ? form.minRating : null,
    additional,
    max_results: form.maxResults,
  };
}

export function rankToMatchScore(rank: number): number {
  return Math.max(60, Math.round(100 - (rank - 1) * 8));
}

export function recommendationToSummary(
  item: {
    restaurant_id: string;
    name: string;
    cuisine: string;
    rating: number | null;
    estimated_cost: string | null;
    rank: number;
  },
  location: string,
): RestaurantSummary {
  return {
    id: item.restaurant_id,
    name: item.name,
    cuisine: item.cuisine,
    location,
    rating: item.rating,
    price_range: null,
    estimated_cost: item.estimated_cost,
    votes: null,
    address: null,
    match_score: rankToMatchScore(item.rank),
  };
}
