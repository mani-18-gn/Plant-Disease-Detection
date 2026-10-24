from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PlantIdentificationSchema(BaseModel):
    common_name: str = "Unknown Plant"
    scientific_name: Optional[str] = None
    certainty: str = "Moderate"  # "High" | "Moderate" | "Low"
    plant_part: str = "Leaf"


class DifferentialDiagnosisItem(BaseModel):
    disease_name: str
    distinguishing_feature: str


class DiseaseAssessmentSchema(BaseModel):
    is_healthy: bool = False
    most_likely_disease: str
    pathogen_scientific_name: Optional[str] = None
    cause: str = "unknown"  # "fungal" | "bacterial" | "viral" | "pest" | "nutritional" | "environmental" | "healthy" | "unknown"
    confidence: str = "Moderate"  # "High" | "Moderate" | "Low"
    confidence_explanation: str
    symptoms_observed: List[str] = Field(default_factory=list)
    plausibility_explanation: str
    differential_diagnosis: List[DifferentialDiagnosisItem] = Field(default_factory=list)


class DiseaseInformationSchema(BaseModel):
    typical_symptoms: str
    favorable_conditions: str


class TreatmentAndManagementSchema(BaseModel):
    immediate_actions: List[str] = Field(default_factory=list)
    cultural_practices: List[str] = Field(default_factory=list)
    biological_control: List[str] = Field(default_factory=list)
    chemical_management: List[str] = Field(default_factory=list)
    safety_precautions: str = "Always wear protective gear and follow manufacturer pesticide labels."
    preventive_measures: List[str] = Field(default_factory=list)


class AgriculturalSourceItem(BaseModel):
    title: str
    organization: str
    url: str
    notes: Optional[str] = None


class GoogleAIDiagnosisBody(BaseModel):
    plant_identification: PlantIdentificationSchema
    disease_assessment: DiseaseAssessmentSchema
    disease_information: DiseaseInformationSchema
    treatment_and_management: TreatmentAndManagementSchema
    uncertainty_disclaimer: str


class DiagnoseAPIResponse(BaseModel):
    status: str  # "success" | "not_a_plant" | "insufficient_evidence" | "api_key_missing" | "api_key_invalid" | "error"
    is_plant: Optional[bool] = None
    image_quality: Optional[str] = "good"
    rejection_reason: Optional[str] = None
    error: Optional[str] = None
    diagnosis: Optional[GoogleAIDiagnosisBody] = None
    sources: List[AgriculturalSourceItem] = Field(default_factory=list)
    model_used: Optional[str] = None
    local_model_comparison: Optional[Dict[str, Any]] = None
