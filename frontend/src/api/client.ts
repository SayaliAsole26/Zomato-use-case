import type {
  LocationsResponse,
  RecommendationApiResponse,
  UserPreferences,
} from "../types/api";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

async function handleResponse<T>(res: Response): Promise<T> {
  let data: unknown;
  try {
    data = await res.json();
  } catch {
    throw new Error(`API error (${res.status}): non-JSON response`);
  }
  if (!res.ok) {
    const body = data as { detail?: string };
    const detail = typeof body.detail === "string" ? body.detail : `HTTP ${res.status}`;
    throw new Error(detail);
  }
  return data as T;
}

export async function fetchLocations(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/v1/locations`);
  const data = await handleResponse<LocationsResponse>(res);
  return data.locations;
}

export async function fetchRecommendations(
  preferences: UserPreferences,
): Promise<RecommendationApiResponse> {
  const res = await fetch(`${API_BASE}/api/v1/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(preferences),
  });
  return handleResponse<RecommendationApiResponse>(res);
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
