interface ErrorStateProps {
  message: string;
  onRetry: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <section className="p-10 bg-surface-container rounded-2xl border border-outline-variant text-center flex flex-col items-center gap-6">
      <span className="material-symbols-outlined text-5xl text-primary">error_outline</span>
      <h2 className="text-2xl font-semibold">Something went wrong</h2>
      <p className="text-base text-on-surface-variant max-w-lg">{message}</p>
      <button type="button" onClick={onRetry} className="btn-primary px-8 py-3 text-sm">
        Retry
      </button>
    </section>
  );
}
