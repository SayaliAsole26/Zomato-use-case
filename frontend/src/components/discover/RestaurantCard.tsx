import type { RecommendationItem } from "../../types/api";
import { PLACEHOLDER_IMAGES } from "../../lib/constants";

interface RestaurantCardProps {
  item: RecommendationItem;
  location: string;
  index: number;
}

export function RestaurantCard({ item, location, index }: RestaurantCardProps) {
  const isTop = item.rank === 1;
  const badgeClass = isTop
    ? "bg-gradient-to-r from-primary to-primary-container text-white"
    : "bg-surface-container-high text-primary";
  const image = PLACEHOLDER_IMAGES[index % PLACEHOLDER_IMAGES.length];

  return (
    <article className="restaurant-card bg-white rounded-2xl p-4 flex flex-col md:flex-row gap-6 border border-transparent shadow-card">
      <div className="relative w-full md:w-64 h-64 shrink-0">
        <img
          src={image}
          alt={item.name}
          className="w-full h-full object-cover rounded-xl"
          loading="lazy"
        />
        <div
          className={`absolute top-2 left-2 ${badgeClass} px-4 py-1 rounded-lg text-sm font-bold shadow-md`}
        >
          #{item.rank} Match
        </div>
      </div>

      <div className="flex-1 flex flex-col py-1 pr-2 min-w-0">
        <div className="flex justify-between items-start mb-2 gap-3">
          <div className="min-w-0">
            <h3 className="text-2xl font-semibold text-on-surface truncate">{item.name}</h3>
            <p className="text-sm font-semibold text-on-surface-variant line-clamp-2">
              {item.cuisine}
            </p>
          </div>
          <div className="flex items-center gap-1 bg-tertiary-container px-2 py-1 rounded-lg shrink-0">
            <span className="material-symbols-outlined filled text-on-tertiary-container text-base">
              star
            </span>
            <span className="text-on-tertiary-container font-bold text-sm">
              {item.rating ?? "N/A"}
            </span>
          </div>
        </div>

        <div className="flex gap-4 mb-4 flex-wrap text-sm font-semibold">
          <span className="text-tertiary">{item.estimated_cost ?? "N/A"}</span>
          <span className="text-on-surface-variant">• {location}</span>
        </div>

        <div className="ai-explanation mt-auto">
          <div className="flex items-center gap-2 mb-1">
            <span className="material-symbols-outlined text-primary text-sm">psychology</span>
            <span className="text-sm font-bold text-on-surface">CulinaAI Reason</span>
          </div>
          <p className="text-base text-on-surface-variant leading-relaxed">
            &ldquo;{item.explanation}&rdquo;
          </p>
        </div>
      </div>
    </article>
  );
}
