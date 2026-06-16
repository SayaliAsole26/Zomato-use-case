import { useMutation } from "@tanstack/react-query";
import { fetchRecommendations, toApiPreferences } from "../services/api";
import type { PreferencesFormState, RecommendationApiResponse } from "../types/api";

export function useRecommendations() {
  return useMutation({
    mutationFn: async (form: PreferencesFormState): Promise<RecommendationApiResponse> => {
      return fetchRecommendations(toApiPreferences(form));
    },
  });
}
