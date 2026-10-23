import apiClient from "./client";

export const advisoryApi = {
  generateAdvisory: (cropBlockId, detectionId = null) =>
    apiClient.post("/api/v1/agents/advisory/generate", {
      crop_block_id: cropBlockId,
      detection_id: detectionId,
    }),
};
