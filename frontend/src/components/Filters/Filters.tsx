import type { Budget, PreferencesFormState } from "../../types/api";

interface FiltersProps {
  form: PreferencesFormState;
  locations: string[];
  loading?: boolean;
  mobileOpen?: boolean;
  onCloseMobile?: () => void;
  onChange: (patch: Partial<PreferencesFormState>) => void;
  onSubmit: () => void;
}

const BUDGETS: { value: Budget; label: string }[] = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
];

export function Filters({
  form,
  locations,
  loading = false,
  mobileOpen = false,
  onCloseMobile,
  onChange,
  onSubmit,
}: FiltersProps) {
  const panel = (
    <aside className="w-full lg:w-80 shrink-0 bg-surface-container-low border-r border-outline-variant p-6 flex flex-col gap-6 overflow-y-auto">
      <div className="flex items-center justify-between lg:hidden">
        <h2 className="text-lg font-semibold">Filters</h2>
        {onCloseMobile && (
          <button type="button" onClick={onCloseMobile} className="material-symbols-outlined">
            close
          </button>
        )}
      </div>

      <div>
        <label htmlFor="location" className="block text-sm font-semibold mb-2">
          Location
        </label>
        <select
          id="location"
          value={form.location}
          onChange={(e) => onChange({ location: e.target.value })}
          className="w-full h-11 px-3 rounded-xl border border-outline-variant bg-white"
        >
          {locations.map((loc) => (
            <option key={loc} value={loc}>
              {loc}
            </option>
          ))}
        </select>
      </div>

      <div>
        <span className="block text-sm font-semibold mb-2">Budget</span>
        <div className="flex gap-2">
          {BUDGETS.map((b) => (
            <button
              key={b.value}
              type="button"
              onClick={() => onChange({ budget: b.value })}
              className={`budget-pill ${form.budget === b.value ? "budget-pill-selected" : ""}`}
            >
              {b.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label htmlFor="cuisine" className="block text-sm font-semibold mb-2">
          Cuisine
        </label>
        <input
          id="cuisine"
          type="text"
          value={form.cuisine}
          onChange={(e) => onChange({ cuisine: e.target.value })}
          placeholder="e.g. North Indian"
          className="w-full h-11 px-3 rounded-xl border border-outline-variant bg-white"
        />
      </div>

      <div>
        <label htmlFor="minRating" className="block text-sm font-semibold mb-2">
          Minimum rating: {form.minRating.toFixed(1)}
        </label>
        <input
          id="minRating"
          type="range"
          min={0}
          max={5}
          step={0.5}
          value={form.minRating}
          onChange={(e) => onChange({ minRating: Number(e.target.value) })}
          className="w-full accent-primary"
        />
      </div>

      <div>
        <label htmlFor="additional" className="block text-sm font-semibold mb-2">
          Additional preferences
        </label>
        <textarea
          id="additional"
          value={form.additional}
          onChange={(e) => onChange({ additional: e.target.value })}
          rows={3}
          placeholder="family-friendly, outdoor seating"
          className="w-full px-3 py-2 rounded-xl border border-outline-variant bg-white resize-none"
        />
      </div>

      <button
        type="button"
        disabled={loading}
        onClick={onSubmit}
        className="btn-primary h-12 w-full flex items-center justify-center gap-2 disabled:opacity-60"
      >
        <span className="material-symbols-outlined filled">auto_awesome</span>
        {loading ? "Searching…" : "Find Restaurants"}
      </button>
    </aside>
  );

  return (
    <>
      <div className="hidden lg:block sticky top-16 h-[calc(100vh-4rem)]">{panel}</div>
      {mobileOpen && (
        <div className="lg:hidden fixed inset-0 z-50 bg-black/40" onClick={onCloseMobile}>
          <div
            className="absolute inset-y-0 left-0 w-[min(100%,20rem)] bg-surface-container-low shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            {panel}
          </div>
        </div>
      )}
    </>
  );
}
