import { useCallback, useEffect, useState } from "react";
import { fetchLocations, fetchRecommendations, toApiPreferences } from "../api/client";
import { EmptyState } from "../components/discover/EmptyState";
import { ErrorState } from "../components/discover/ErrorState";
import { LoadingState } from "../components/discover/LoadingState";
import { PreferencesSidebar } from "../components/discover/PreferencesSidebar";
import { RestaurantCard } from "../components/discover/RestaurantCard";
import { Footer } from "../components/layout/Footer";
import { Header } from "../components/layout/Header";
import { DEMO_LOCATION } from "../lib/constants";
import type {
  PreferencesFormState,
  RecommendationApiResponse,
} from "../types/api";

type ViewState = "welcome" | "loading" | "results" | "empty" | "error";

const DEFAULT_FORM: PreferencesFormState = {
  location: DEMO_LOCATION,
  budget: "medium",
  cuisine: "North Indian",
  minRating: 4.0,
  maxResults: 5,
  additional: "",
};

function formatMeta(meta: RecommendationApiResponse["meta"]): string {
  if (!meta) return "";
  const seconds =
    meta.latency_ms != null ? `${(meta.latency_ms / 1000).toFixed(1)}s` : "—";
  return `Considered ${meta.candidates_considered} restaurants · ${seconds} processing time`;
}

function formatSummary(data: RecommendationApiResponse, form: PreferencesFormState): string {
  if (data.summary) return data.summary;
  const cuisinePart = form.cuisine ? `${form.cuisine}-friendly ` : "";
  const ratingPart = form.minRating > 0 ? ` and ${form.minRating}+ rating` : "";
  return `Top picks for ${cuisinePart}restaurants in ${form.location} within your ${form.budget} budget${ratingPart}.`;
}

export function DiscoverPage() {
  const [locations, setLocations] = useState<string[]>([]);
  const [form, setForm] = useState<PreferencesFormState>(DEFAULT_FORM);
  const [view, setView] = useState<ViewState>("welcome");
  const [result, setResult] = useState<RecommendationApiResponse | null>(null);
  const [error, setError] = useState<string>("");
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);
  const [initError, setInitError] = useState<string | null>(null);

  useEffect(() => {
    fetchLocations()
      .then((locs) => {
        setLocations(locs);
        const preferred = locs.includes(DEMO_LOCATION) ? DEMO_LOCATION : locs[0];
        setForm((f) => ({ ...f, location: preferred ?? f.location }));
      })
      .catch(() => setInitError("Could not load restaurant dataset. Is the API server running?"));
  }, []);

  const patchForm = useCallback((patch: Partial<PreferencesFormState>) => {
    setForm((prev) => ({ ...prev, ...patch }));
  }, []);

  const runSearch = useCallback(async () => {
    setView("loading");
    setError("");
    try {
      const data = await fetchRecommendations(toApiPreferences(form));
      setResult(data);
      if (!data.recommendations.length) {
        setView("empty");
      } else {
        setView("results");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
      setView("error");
    }
  }, [form]);

  const handleSuggestion = (tip: string) => {
    const lower = tip.toLowerCase();
    if (lower.includes("location")) {
      document.getElementById("location")?.focus();
    } else if (lower.includes("budget")) {
      patchForm({ budget: "medium" });
    } else if (lower.includes("cuisine")) {
      patchForm({ cuisine: "" });
    } else if (lower.includes("rating")) {
      patchForm({ minRating: 3.0 });
    }
  };

  if (initError) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 p-8 max-w-container-max mx-auto w-full">
          <ErrorState message={initError} onRetry={() => window.location.reload()} />
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header onOpenFilters={() => setMobileFiltersOpen(true)} />

      {result?.meta?.fallback && (
        <div className="bg-error-container text-on-error-container text-sm px-6 py-2 text-center">
          Showing top-rated matches from your filters (AI was unavailable or returned invalid
          JSON).
        </div>
      )}

      <div className="max-w-container-max mx-auto flex flex-1 w-full">
        <PreferencesSidebar
          form={form}
          locations={locations}
          loading={view === "loading"}
          mobileOpen={mobileFiltersOpen}
          onCloseMobile={() => setMobileFiltersOpen(false)}
          onChange={patchForm}
          onSubmit={runSearch}
        />

        <main className="flex-1 min-w-0 p-6 lg:p-10">
          {view === "welcome" && (
            <section className="mb-8">
              <div className="p-6 lg:p-8 bg-surface-container rounded-2xl border border-outline-variant flex flex-col gap-3">
                <div className="flex items-center gap-2 text-primary">
                  <span className="material-symbols-outlined filled">auto_awesome</span>
                  <h1 className="text-2xl font-semibold">Discover Restaurants</h1>
                </div>
                <p className="text-lg text-on-surface leading-relaxed">
                  Set your preferences and click <strong>Find Restaurants</strong>. CulinaAI
                  filters real Zomato data, then explains each pick.
                </p>
                <p className="text-sm text-on-surface-variant">
                  <strong>Demo:</strong> BTM · Medium · North Indian · 4.0+ rating
                </p>
              </div>
            </section>
          )}

          {view === "loading" && <LoadingState />}

          {view === "error" && <ErrorState message={error} onRetry={runSearch} />}

          {view === "empty" && result && (
            <EmptyState
              message={result.message ?? "No restaurants match your preferences."}
              suggestions={result.suggestions ?? []}
              onSuggestion={handleSuggestion}
            />
          )}

          {view === "results" && result && (
            <section>
              <div className="p-6 lg:p-8 bg-surface-container rounded-2xl border border-outline-variant flex flex-col gap-3 mb-8">
                <div className="flex items-center gap-2 text-primary">
                  <span className="material-symbols-outlined filled">auto_awesome</span>
                  <h2 className="text-2xl font-semibold">Search Results</h2>
                </div>
                <p className="text-lg text-on-surface leading-relaxed">
                  {formatSummary(result, form)}
                </p>
              </div>
              <div className="flex flex-col gap-8">
                {result.recommendations.map((item, index) => (
                  <RestaurantCard
                    key={item.restaurant_id}
                    item={item}
                    location={form.location}
                    index={index}
                  />
                ))}
              </div>
            </section>
          )}
        </main>
      </div>

      <Footer metaText={result ? formatMeta(result.meta) : undefined} />
    </div>
  );
}
