export function LoadingState() {
  return (
    <section className="mb-8">
      <div className="p-6 bg-surface-container rounded-2xl border border-outline-variant mb-6">
        <div className="flex items-center gap-3 text-primary">
          <span className="material-symbols-outlined animate-spin">progress_activity</span>
          <p className="text-lg">Finding the best matches for you…</p>
        </div>
      </div>
      <div className="flex flex-col gap-8">
        <div className="h-64 rounded-2xl bg-surface-container-high animate-pulse" />
        <div className="h-64 rounded-2xl bg-surface-container-high animate-pulse" />
      </div>
    </section>
  );
}
