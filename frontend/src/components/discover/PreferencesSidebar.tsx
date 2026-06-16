import type { Budget, PreferencesFormState } from "../../types/api";
import { CUISINE_CHIPS } from "../../lib/constants";

interface PreferencesSidebarProps {
  form: PreferencesFormState;
  locations: string[];
  loading: boolean;
  mobileOpen: boolean;
  onCloseMobile: () => void;
  onChange: (patch: Partial<PreferencesFormState>) => void;
  onSubmit: () => void;
}

const BUDGETS: { value: Budget; label: string }[] = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
];

export function PreferencesSidebar({
  form,
  locations,
  loading,
  mobileOpen,
  onCloseMobile,
  onChange,
  onSubmit,
}: PreferencesSidebarProps) {
  const panelClass = [
    "flex flex-col p-6 gap-6 border-r border-outline-variant bg-surface-container-low",
    "w-80 shrink-0 lg:sticky lg:top-16 lg:self-start lg:h-[calc(100vh-4rem)] lg:overflow-y-auto",
    mobileOpen
      ? "fixed inset-0 z-40 lg:relative lg:inset-auto"
      : "hidden lg:flex",
  ].join(" ");

  return (
    <>
      {mobileOpen && (
        <button
          type="button"
          className="fixed inset-0 bg-black/30 z-30 lg:hidden"
          onClick={onCloseMobile}
          aria-label="Close filters"
        />
      )}

      <aside className={panelClass}>
        <div className="flex items-center justify-between lg:block">
          <div>
            <h2 className="text-2xl font-semibold text-primary">Preferences</h2>
            <p className="text-sm font-semibold text-on-surface-variant">Fine-tune your search</p>
          </div>
          <button
            type="button"
            className="lg:hidden material-symbols-outlined text-on-surface-variant"
            onClick={onCloseMobile}
          >
            close
          </button>
        </div>

        <form
          className="flex flex-col gap-6 flex-1"
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit();
            onCloseMobile();
          }}
        >
          <div className="flex flex-col gap-1">
            <label htmlFor="location" className="text-sm font-semibold text-on-surface-variant">
              Location
            </label>
            <select
              id="location"
              value={form.location}
              onChange={(e) => onChange({ location: e.target.value })}
              className="w-full bg-surface border border-outline-variant rounded-xl p-3 text-base focus:ring-primary focus:border-primary"
            >
              {locations.map((loc) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </select>
            <p className="text-xs text-on-surface-variant">
              Bangalore area names (e.g. BTM, Banashankari)
            </p>
          </div>

          <div className="flex flex-col gap-2">
            <span className="text-sm font-semibold text-on-surface-variant">Budget</span>
            <div className="flex gap-2">
              {BUDGETS.map(({ value, label }) => (
                <button
                  key={value}
                  type="button"
                  className={`budget-pill ${form.budget === value ? "budget-pill-selected" : ""}`}
                  onClick={() => onChange({ budget: value })}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <label htmlFor="cuisine" className="text-sm font-semibold text-on-surface-variant">
              Cuisine
            </label>
            <input
              id="cuisine"
              type="text"
              value={form.cuisine}
              placeholder="e.g. North Indian"
              onChange={(e) => onChange({ cuisine: e.target.value })}
              className="w-full bg-surface border border-outline-variant rounded-xl p-3 text-base focus:ring-primary focus:border-primary"
            />
            <div className="flex flex-wrap gap-2">
              {CUISINE_CHIPS.map((c) => (
                <button
                  key={c}
                  type="button"
                  className={`chip ${form.cuisine === c ? "chip-selected" : ""}`}
                  onClick={() => onChange({ cuisine: form.cuisine === c ? "" : c })}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <div className="flex justify-between items-center">
              <label htmlFor="min-rating" className="text-sm font-semibold text-on-surface-variant">
                Min Rating
              </label>
              <span className="text-sm font-bold text-primary">{form.minRating.toFixed(1)}+</span>
            </div>
            <input
              id="min-rating"
              type="range"
              min={0}
              max={5}
              step={0.5}
              value={form.minRating}
              onChange={(e) => onChange({ minRating: parseFloat(e.target.value) })}
              className="w-full h-2 bg-surface-container-high rounded-lg appearance-none cursor-pointer accent-primary"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label htmlFor="additional" className="text-sm font-semibold text-on-surface-variant">
              Additional preferences
            </label>
            <textarea
              id="additional"
              rows={2}
              value={form.additional}
              placeholder="family-friendly, quick service"
              onChange={(e) => onChange({ additional: e.target.value })}
              className="w-full bg-surface border border-outline-variant rounded-xl p-3 text-base focus:ring-primary focus:border-primary resize-none"
            />
          </div>

          <div className="flex flex-col gap-2">
            <span className="text-sm font-semibold text-on-surface-variant">Max Results</span>
            <div className="flex items-center border border-outline-variant rounded-xl overflow-hidden">
              <button
                type="button"
                className="p-3 hover:bg-surface-container-high transition-all"
                onClick={() => onChange({ maxResults: Math.max(1, form.maxResults - 1) })}
              >
                <span className="material-symbols-outlined">remove</span>
              </button>
              <span className="w-full text-center font-bold">{form.maxResults}</span>
              <button
                type="button"
                className="p-3 hover:bg-surface-container-high transition-all"
                onClick={() => onChange({ maxResults: Math.min(10, form.maxResults + 1) })}
              >
                <span className="material-symbols-outlined">add</span>
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full py-4 text-xl disabled:opacity-60"
          >
            {loading ? "Searching…" : "Find Restaurants"}
          </button>
        </form>

        <div className="mt-auto pt-6 border-t border-outline-variant">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center text-on-primary">
              <span className="material-symbols-outlined">person</span>
            </div>
            <div>
              <p className="text-sm font-semibold">Foodie Navigator</p>
              <p className="text-xs text-on-surface-variant">Bangalore, IN</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
