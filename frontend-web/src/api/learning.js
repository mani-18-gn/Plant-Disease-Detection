import apiClient from "./client";

export const learningApi = {
  submitFeedback: (advisoryId, rating, outcomeNotes = null) =>
    apiClient.post("/api/v1/agents/learning/feedback", {
      advisory_id: advisoryId,
      rating,
      outcome_notes: outcomeNotes,
    }),

  getCropBlockSummary: (cropBlockId) =>
    apiClient.get(`/api/v1/agents/learning/summary/crop_block/${cropBlockId}`),

  getScore: (stateKey, actionKey) =>
    apiClient.get("/api/v1/agents/learning/score", {
      params: { state_key: stateKey, action_key: actionKey },
    }),
};
