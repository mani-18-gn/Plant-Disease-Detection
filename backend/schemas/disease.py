import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DiseaseDetectionCreate(BaseModel):
    crop_block_id: uuid.UUID
    image_path: str
    predicted_disease: str
    cnn_confidence: float
    posterior_probability: float | None = None
    validated: bool = False


class DiseaseDetectionResponse(BaseModel):
    id: uuid.UUID
    crop_block_id: uuid.UUID | None = None
    image_path: str
    predicted_disease: str
    cnn_confidence: float
    posterior_probability: float | None = None
    validated: bool = False
    detected_at: datetime

    # Enriched Multi-Crop Botanical and Pathological Monograph
    crop: str | None = None
    crop_kn: str | None = None
    scientific_name: str | None = None
    condition: str | None = None
    condition_kn: str | None = None
    affected_parts: list[str] | None = None
    is_healthy: bool | None = None
    is_inconclusive: bool = False
    causal_agent: str | None = None
    symptoms: str | None = None
    symptoms_kn: str | None = None
    differential_diagnosis: str | None = None
    differential_diagnosis_kn: str | None = None
    favorable_conditions: str | None = None
    favorable_conditions_kn: str | None = None
    preventive_practices: str | None = None
    preventive_practices_kn: str | None = None
    cultural_biological_management: str | None = None
    cultural_biological_management_kn: str | None = None
    chemical_management: str | None = None
    chemical_management_kn: str | None = None
    expert_warning: str | None = None
    expert_warning_kn: str | None = None
    management: str | None = None
    management_kn: str | None = None
    sources: list[dict] | None = None
    top_predictions: list[dict] | None = None
    backend: str | None = None

    # Multi-Stage Pipeline Safety Flags
    is_plant: bool = True
    plant_coverage_pct: float | None = None
    plausibility_note: str | None = None
    image_quality: dict | None = None
    crop_match: bool | None = None
    crop_mismatch_warning: str | None = None
    crop_support_status: str | None = None
    identification_rationale: str | None = None

    # Multi-Stage Corroborating Evidence (Online Research & Visual Prototype Retrieval)
    online_research: list[dict] | None = None
    visual_similarity: list[dict] | None = None

    model_config = ConfigDict(from_attributes=True)
