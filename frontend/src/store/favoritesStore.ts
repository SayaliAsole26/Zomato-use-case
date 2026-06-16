import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { RestaurantSummary } from "../types/api";

interface FavoritesState {
  saved: RestaurantSummary[];
  toggle: (restaurant: RestaurantSummary) => void;
  remove: (id: string) => void;
  isSaved: (id: string) => boolean;
}

export const useFavoritesStore = create<FavoritesState>()(
  persist(
    (set, get) => ({
      saved: [],
      toggle: (restaurant) => {
        const exists = get().saved.some((r) => r.id === restaurant.id);
        set({
          saved: exists
            ? get().saved.filter((r) => r.id !== restaurant.id)
            : [...get().saved, restaurant],
        });
      },
      remove: (id) => set({ saved: get().saved.filter((r) => r.id !== id) }),
      isSaved: (id) => get().saved.some((r) => r.id === id),
    }),
    { name: "culinaai-favorites" },
  ),
);
