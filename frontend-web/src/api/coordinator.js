import apiClient from "./client";

export const coordinatorApi = {
  synthesizeStatus: (cropBlockId, detectionId = null) =>
    apiClient.post("/api/v1/agents/coordinator/synthesize", {
      crop_block_id: cropBlockId,
      detection_id: detectionId,
    }),
};
