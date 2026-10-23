import apiClient from "./client";

export const weatherApi = {
  getCurrentWeather: (farmId, forceRefresh = false) => {
    return apiClient.get(`/api/v1/agents/weather/current/${farmId}`, {
      params: { force_refresh: forceRefresh },
    });
  },
};
