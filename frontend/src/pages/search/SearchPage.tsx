import { useCallback, useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { EmptyState } from "../../components/EmptyState/EmptyState";
import { Filters } from "../../components/Filters/Filters";
import { PopularRestaurants } from "../../components/PopularRestaurants/PopularRestaurants";
import {
  RestaurantCard,
  recommendationToCardProps,
} from "../../components/RestaurantCard/RestaurantCard";
import { SearchBar } from "../../components/SearchBar/SearchBar";
import { LoadingState } from "../../components/discover/LoadingState";
import { ErrorState } from "../../components/discover/ErrorState";
import { useRecommendations } from "../../hooks/useRecommendations";
import { AppLayout } from "../../layouts/AppLayout";
import { DEMO_LOCATION } from "../../lib/constants";
import { fetchLocations, recommendationToSummary } from "../../services/api";
import { useFavoritesStore } from "../../store/favoritesStore";
import { DEFAULT_FORM, useSearchStore } from "../../store/searchStore";
import type { RecommendationApiResponse } from "../../types/api";

type ViewState = "welcome" | "loading" | "results" | "empty" | "error";

function formatMeta(meta: RecommendationApiResponse["meta"]): string {
  if (!meta) return "";
  const seconds =
    meta.latency_ms != null ? `${(meta.latency_ms / 1000).toFixed(1)}s` : "—";
  return `Considered ${meta.candidates_considered} restaurants · ${seconds} processing time`;
}

function formatSummary(
  data: RecommendationApiResponse,
  form: typeof DEFAULT_FORM,
): string {
  if (data.summary) return data.summary;
  const cuisinePart = form.cuisine ? `${form.cuisine}-friendly ` : "";
  const ratingPart = form.minRating > 0 ? ` and ${form.minRating}+ rating` : "";
  return `Top picks for ${cuisinePart}restaurants in ${form.location} within your ${form.budget} budget${ratingPart}.`;
}

export function SearchPage() {
  const form = useSearchStore((s) => s.form);
  const setForm = useSearchStore((s) => s.setForm);
  const toggleFavorite = useFavoritesStore((s) => s.toggle);
  const isSaved = useFavoritesStore((s) => s.isSaved);
  const recommend = useRecommendations();

  const [view, setView] = useState<ViewState>("welcome");
  const [result, setResult] = useState<RecommendationApiResponse | null>(null);
  const [error, setError] = useState("");
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const { data: locations = [], error: locError } = useQuery({
    queryKey: ["locations"],
    queryFn: fetchLocations,
  });

  useEffect(() => {
    if (locations.length && !locations.includes(form.location)) {
      const preferred = locations.includes(DEMO_LOCATION) ? DEMO_LOCATION : locations[0];
      setForm({ location: preferred });
    }
  }, [locations, form.location, setForm]);

  const patchForm = useCallback(
    (patch: Partial<typeof form>) => setForm(patch),
    [setForm],
  );

  const runSearch = useCallback(async () => {
    if (searchQuery.trim()) {
      patchForm({ cuisine: searchQuery.trim() });
    }
    setView("loading");
    setError("");
    try {
      const data = await recommend.mutateAsync(form);
      setResult(data);
      setView(data.recommendations.length ? "results" : "empty");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
      setView("error");
    }
  }, [form, patchForm, recommend, searchQuery]);

  const handleShare = (name: string) => {
    const text = `Check out ${name} on CulinaAI`;
    if (navigator.share) {
      navigator.share({ title: "CulinaAI", text }).catch(() => undefined);
    } else {
      navigator.clipboard.writeText(text);
    }
  };

  const handleSuggestion = (tip: string) => {
    const lower = tip.toLowerCase();
    if (lower.includes("location")) document.getElementById("location")?.focus();
    else if (lower.includes("budget")) patchForm({ budget: "medium" });
    else if (lower.includes("cuisine")) patchForm({ cuisine: "" });
    else if (lower.includes("rating")) patchForm({ minRating: 3.0 });
  };

  if (locError) {
    return (
      <AppLayout>
        <main className="flex-1 p-8 max-w-container-max mx-auto w-full">
          <ErrorState
            message="Could not load restaurant dataset. Is the API server running?"
            onRetry={() => window.location.reload()}
          />
        </main>
      </AppLayout>
    );
  }

  return (
    <AppLayout
      onOpenFilters={() => setMobileFiltersOpen(true)}
      footerMeta={result ? formatMeta(result.meta) : undefined}
    >
      {result?.meta?.fallback && (
        <div className="bg-error-container text-on-error-container text-sm px-6 py-2 text-center">
          Showing top-rated matches from your filters (AI was unavailable).
        </div>
      )}

      <div className="max-w-container-max mx-auto flex flex-1 w-full">
        <Filters
          form={form}
          locations={locations}
          loading={view === "loading"}
          mobileOpen={mobileFiltersOpen}
          onCloseMobile={() => setMobileFiltersOpen(false)}
          onChange={patchForm}
          onSubmit={runSearch}
        />

        <main className="flex-1 min-w-0 p-6 lg:p-10">
          <div className="mb-6">
            <SearchBar value={searchQuery} onChange={setSearchQuery} onSubmit={runSearch} />
          </div>

          {view === "welcome" && (
            <>
              <section className="mb-8">
                <div className="p-6 lg:p-8 bg-surface-container rounded-2xl border border-outline-variant flex flex-col gap-3">
                  <div className="flex items-center gap-2 text-primary">
                    <span className="material-symbols-outlined filled">auto_awesome</span>
                    <h1 className="text-2xl font-semibold">Search Restaurants</h1>
                  </div>
                  <p className="text-lg text-on-surface leading-relaxed">
                    Set filters or use the search bar, then get AI-explained recommendations.
                  </p>
                </div>
              </section>
              <PopularRestaurants location={form.location} />
            </>
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
                  <h2 className="text-2xl font-semibold">Recommendation Results</h2>
                </div>
                <p className="text-lg text-on-surface leading-relaxed">
                  {formatSummary(result, form)}
                </p>
              </div>
              <div className="flex flex-col gap-8">
                {result.recommendations.map((item, index) => {
                  const props = recommendationToCardProps(item, form.location, index);
                  return (
                    <RestaurantCard
                      key={item.restaurant_id}
                      {...props}
                      saved={isSaved(item.restaurant_id)}
                      onSave={() =>
                        toggleFavorite(recommendationToSummary(item, form.location))
                      }
                      onShare={() => handleShare(item.name)}
                    />
                  );
                })}
              </div>
            </section>
          )}
        </main>
      </div>
    </AppLayout>
  );
}
