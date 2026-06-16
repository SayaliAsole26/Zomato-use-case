interface EmptyStateProps {
  message: string;
  suggestions: string[];
  onSuggestion: (tip: string) => void;
}

export function EmptyState({ message, suggestions, onSuggestion }: EmptyStateProps) {
  return (
    <section className="p-10 bg-surface-container rounded-2xl border border-outline-variant text-center flex flex-col items-center gap-6">
      <div className="w-24 h-24 rounded-full bg-surface-variant flex items-center justify-center">
        <span className="material-symbols-outlined text-4xl text-on-surface-variant">
          search_off
        </span>
      </div>
      <h2 className="text-2xl font-semibold">No restaurants match your preferences</h2>
      <p className="text-base text-on-surface-variant max-w-lg">{message}</p>
      <div className="ai-explanation text-left max-w-lg w-full">
        <div className="flex items-center gap-2 mb-1">
          <span className="material-symbols-outlined text-primary text-sm filled">
            auto_awesome
          </span>
          <span className="text-sm font-bold">CulinaAI Insight</span>
        </div>
        <p className="text-base text-on-surface-variant">
          Try broadening your filters — location, budget, cuisine, or minimum rating.
        </p>
      </div>
      <div className="flex flex-wrap justify-center gap-2">
        {suggestions.map((tip) => (
          <button
            key={tip}
            type="button"
            onClick={() => onSuggestion(tip)}
            className="chip"
          >
            {tip}
          </button>
        ))}
      </div>
    </section>
  );
}
