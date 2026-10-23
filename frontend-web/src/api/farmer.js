import apiClient from "./client";

export const farmerApi = {
  // Farmer Profile
  getProfile: () => apiClient.get("/api/v1/core/profile"),

  createProfile: (data) => apiClient.post("/api/v1/core/profile", data),

  updateProfile: (data) => apiClient.put("/api/v1/core/profile", data),

  // Farms
  listFarms: () => apiClient.get("/api/v1/core/farms"),

  createFarm: (data) => apiClient.post("/api/v1/core/farms", data),

  updateFarm: (farmId, data) => apiClient.put(`/api/v1/core/farms/${farmId}`, data),

  // Crop Blocks
  listCropBlocks: (farmId) => apiClient.get(`/api/v1/core/farms/${farmId}/crop-blocks`),

  createCropBlock: (farmId, data) =>
    apiClient.post("/api/v1/core/crop-blocks", { ...data, farm_id: farmId }),

  updateCropBlock: (cropBlockId, data) =>
    apiClient.put(`/api/v1/core/crop-blocks/${cropBlockId}`, data),
};
