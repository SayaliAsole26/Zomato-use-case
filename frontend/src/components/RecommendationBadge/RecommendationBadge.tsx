interface RecommendationBadgeProps {
  rank?: number;
  matchScore?: number | null;
  variant?: "primary" | "neutral";
}

export function RecommendationBadge({
  rank,
  matchScore,
  variant = "primary",
}: RecommendationBadgeProps) {
  const label =
    matchScore != null
      ? `${Math.round(matchScore)}% Match`
      : rank != null
        ? `#${rank} Match`
        : "AI Pick";

  const className =
    variant === "primary"
      ? "bg-gradient-to-r from-primary to-primary-container text-white"
      : "bg-surface-container-high text-primary";

  return (
    <div
      className={`inline-flex items-center gap-1 px-4 py-1 rounded-lg text-sm font-bold shadow-md ${className}`}
    >
      <span className="material-symbols-outlined filled text-sm">auto_awesome</span>
      {label}
    </div>
  );
}
