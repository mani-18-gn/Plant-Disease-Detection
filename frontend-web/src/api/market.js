import apiClient from "./client";

export const marketApi = {
  getPrices: (mandiName) => {
    const params = {};
    if (mandiName) {
      params.mandi = mandiName;
      params.mandi_name = mandiName;
    }
    return apiClient.get("/api/v1/agents/market/prices", { params });
  },
};
