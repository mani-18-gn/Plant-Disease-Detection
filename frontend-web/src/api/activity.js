import apiClient from "./client";

export const activityApi = {
  listActivities: (cropBlockId, params = {}) =>
    apiClient.get(`/api/v1/core/crop-blocks/${cropBlockId}/activities`, { params }),

  logActivity: (data) =>
    apiClient.post("/api/v1/core/activities", data),
};
