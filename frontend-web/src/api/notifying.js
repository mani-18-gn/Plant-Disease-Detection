import apiClient from "./client";

export const notifyingApi = {
  sendNotification: (farmerId, content, channel = "in_app") =>
    apiClient.post("/api/v1/agents/notifying/send", {
      farmer_id: farmerId,
      content,
      channel,
    }),

  listNotifications: (farmerId, unreadOnly = false) =>
    apiClient.get(`/api/v1/agents/notifying/${farmerId}`, {
      params: { unread_only: unreadOnly },
    }),

  getHealth: () => apiClient.get("/api/v1/agents/notifying/health"),
};
