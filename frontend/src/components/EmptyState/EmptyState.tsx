interface EmptyStateProps {
  message: string;
  suggestions?: string[];
  onSuggestion?: (tip: string) => void;
}

export function EmptyState({ message, suggestions = [], onSuggestion }: EmptyStateProps) {
  return (
    <section className="flex flex-col items-center text-center py-16 px-6">
      <div className="w-24 h-24 rounded-full bg-surface-container-high flex items-center justify-center mb-6">
        <span className="material-symbols-outlined text-5xl text-primary">search_off</span>
      </div>
      <h2 className="text-2xl font-semibold mb-3">No matches found</h2>
      <p className="text-on-surface-variant max-w-md mb-6">{message}</p>
      {suggestions.length > 0 && (
        <div className="flex flex-col gap-2 w-full max-w-md">
          <p className="text-sm font-semibold text-on-surface">AI suggestions:</p>
          {suggestions.map((tip) => (
            <button
              key={tip}
              type="button"
              onClick={() => onSuggestion?.(tip)}
              className="chip text-left w-full"
            >
              {tip}
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
