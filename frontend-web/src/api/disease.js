import apiClient from "./client";

export const diseaseApi = {
  // Vision Agent: Image upload for CNN multi-crop detection
  detectDisease: (cropBlockId, imageFile, cropType = null, symptoms = null, location = null) => {
    const formData = new FormData();
    if (cropBlockId) {
      formData.append("crop_block_id", cropBlockId);
    }
    if (cropType) {
      formData.append("crop_type", cropType);
    }
    if (symptoms) {
      formData.append("symptoms", symptoms);
    }
    if (location) {
      formData.append("location", location);
    }
    formData.append("file", imageFile);

    return apiClient.post("/api/v1/agents/vision/detect", formData, {
      headers: {
        "Content-Type": undefined,
      },
      timeout: 90000,
    });
  },

  // Get Vision Agent status and supported crops
  getVisionStatus: () => apiClient.get("/api/v1/agents/vision/status"),

  // Benchmark Labeled Samples for instant 1-click evaluation
  getSampleImages: () => apiClient.get("/api/v1/agents/vision/sample-images"),

  // Agricultural Knowledge Base
  getKnowledgeBase: (params) => apiClient.get("/api/v1/agents/vision/knowledge-base", { params }),
  getKnowledgeBaseCrops: () => apiClient.get("/api/v1/agents/vision/knowledge-base/crops"),
  getKnowledgeBaseDetail: (rawKey) => apiClient.get(`/api/v1/agents/vision/knowledge-base/${encodeURIComponent(rawKey)}`),

  // Diagnosis Agent: Bayesian posterior validation with weather and regional priors
  validateDetection: (detectionId) =>
    apiClient.post(`/api/v1/agents/diagnosis/validate/${detectionId}`),

  // Get historical diagnoses for crop block
  getHistory: (cropBlockId) =>
    apiClient.get(`/api/v1/agents/vision/history/${cropBlockId}`),

  // Google-Powered Plant Disease Diagnosis endpoint (POST /api/diagnose)
  diagnoseWithGoogleAI: (imageFile, cropName = null, symptoms = null, location = null, cropBlockId = null) => {
    const formData = new FormData();
    formData.append("file", imageFile);
    if (cropName) formData.append("crop_name", cropName);
    if (symptoms) formData.append("symptoms", symptoms);
    if (location) formData.append("location", location);
    if (cropBlockId) formData.append("crop_block_id", cropBlockId);

    return apiClient.post("/api/diagnose", formData, {
      headers: { "Content-Type": undefined },
      timeout: 90000,
    });
  },

  // Google AI Agent configuration status
  getGoogleAIStatus: () => apiClient.get("/api/diagnose/status"),
};
