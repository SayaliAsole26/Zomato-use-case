import { create } from "zustand";
import type { PreferencesFormState, RecommendationApiResponse } from "../types/api";

interface SearchState {
  form: PreferencesFormState;
  lastResult: RecommendationApiResponse | null;
  setForm: (patch: Partial<PreferencesFormState>) => void;
  setLastResult: (result: RecommendationApiResponse | null) => void;
  resetForm: () => void;
}

export const DEFAULT_FORM: PreferencesFormState = {
  location: "BTM",
  budget: "medium",
  cuisine: "North Indian",
  minRating: 4.0,
  maxResults: 5,
  additional: "",
};

export const useSearchStore = create<SearchState>((set) => ({
  form: DEFAULT_FORM,
  lastResult: null,
  setForm: (patch) => set((s) => ({ form: { ...s.form, ...patch } })),
  setLastResult: (result) => set({ lastResult: result }),
  resetForm: () => set({ form: DEFAULT_FORM }),
}));
