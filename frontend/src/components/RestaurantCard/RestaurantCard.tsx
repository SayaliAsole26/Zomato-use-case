import type { RecommendationItem, RestaurantSummary } from "../../types/api";
import { rankToMatchScore } from "../../services/api";
import { PLACEHOLDER_IMAGES } from "../../lib/constants";
import { AIReasoningCard } from "../AIReasoningCard/AIReasoningCard";
import { RecommendationBadge } from "../RecommendationBadge/RecommendationBadge";

interface RestaurantCardProps {
  id: string;
  name: string;
  cuisine: string;
  rating: number | null;
  location: string;
  estimatedCost?: string | null;
  imageIndex?: number;
  aiReason?: string;
  matchScore?: number | null;
  rank?: number;
  saved?: boolean;
  onSave?: () => void;
  onShare?: () => void;
}

export function RestaurantCard({
  id,
  name,
  cuisine,
  rating,
  location,
  estimatedCost,
  imageIndex = 0,
  aiReason,
  matchScore,
  rank,
  saved = false,
  onSave,
  onShare,
}: RestaurantCardProps) {
  const image = PLACEHOLDER_IMAGES[imageIndex % PLACEHOLDER_IMAGES.length];
  const score = matchScore ?? (rank != null ? rankToMatchScore(rank) : null);

  return (
    <article
      id={`restaurant-${id}`}
      className="restaurant-card bg-white rounded-2xl p-4 flex flex-col md:flex-row gap-6 border border-transparent shadow-card"
    >
      <div className="relative w-full md:w-64 h-64 shrink-0">
        <img
          src={image}
          alt={name}
          className="w-full h-full object-cover rounded-xl"
          loading="lazy"
        />
        <div className="absolute top-2 left-2">
          <RecommendationBadge rank={rank} matchScore={score} />
        </div>
      </div>

      <div className="flex-1 flex flex-col py-1 pr-2 min-w-0">
        <div className="flex justify-between items-start mb-2 gap-3">
          <div className="min-w-0">
            <h3 className="text-2xl font-semibold text-on-surface truncate">{name}</h3>
            <p className="text-sm font-semibold text-on-surface-variant line-clamp-2">{cuisine}</p>
          </div>
          <div className="flex items-center gap-1 bg-tertiary-container px-2 py-1 rounded-lg shrink-0">
            <span className="material-symbols-outlined filled text-on-tertiary-container text-base">
              star
            </span>
            <span className="text-on-tertiary-container font-bold text-sm">{rating ?? "N/A"}</span>
          </div>
        </div>

        <div className="flex gap-4 mb-4 flex-wrap text-sm font-semibold">
          <span className="text-tertiary">{estimatedCost ?? "N/A"}</span>
          <span className="text-on-surface-variant">• {location}</span>
        </div>

        {aiReason && <AIReasoningCard reason={aiReason} />}

        <div className="flex flex-wrap gap-3 mt-4 pt-4 border-t border-outline-variant">
          <button type="button" className="btn-primary px-4 py-2 text-sm">
            Book Table
          </button>
          {onSave && (
            <button
              type="button"
              onClick={onSave}
              className="chip flex items-center gap-1"
              aria-pressed={saved}
            >
              <span className="material-symbols-outlined text-base">
                {saved ? "favorite" : "favorite_border"}
              </span>
              {saved ? "Saved" : "Save"}
            </button>
          )}
          {onShare && (
            <button type="button" onClick={onShare} className="chip flex items-center gap-1">
              <span className="material-symbols-outlined text-base">share</span>
              Share
            </button>
          )}
        </div>
      </div>
    </article>
  );
}

export function recommendationToCardProps(
  item: RecommendationItem,
  location: string,
  index: number,
): RestaurantCardProps {
  return {
    id: item.restaurant_id,
    name: item.name,
    cuisine: item.cuisine,
    rating: item.rating,
    location,
    estimatedCost: item.estimated_cost,
    imageIndex: index,
    aiReason: item.explanation,
    rank: item.rank,
  };
}

export function summaryToCardProps(
  item: RestaurantSummary,
  index: number,
): RestaurantCardProps {
  return {
    id: item.id,
    name: item.name,
    cuisine: item.cuisine,
    rating: item.rating,
    location: item.location,
    estimatedCost: item.estimated_cost,
    imageIndex: index,
    matchScore: item.match_score,
  };
}
