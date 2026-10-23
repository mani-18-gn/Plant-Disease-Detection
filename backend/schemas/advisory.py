import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.db.models.logs.advisory import AdvisoryPriority, AdvisorySource


class AdvisoryGenerateRequest(BaseModel):
    crop_block_id: uuid.UUID


class AdvisoryCreate(BaseModel):
    farmer_id: uuid.UUID
    crop_block_id: uuid.UUID | None = None
    priority: AdvisoryPriority = AdvisoryPriority.MEDIUM
    message: str
    generated_by: AdvisorySource = AdvisorySource.GEMINI
    input_snapshot: dict | None = None


class FeedbackCreate(BaseModel):
    advisory_id: uuid.UUID
    farmer_id: uuid.UUID
    rating: int  # 1-5
    outcome_notes: str | None = None


class AdvisoryResponse(BaseModel):
    id: uuid.UUID
    farmer_id: uuid.UUID
    crop_block_id: uuid.UUID | None = None
    priority: AdvisoryPriority
    message: str
    generated_by: AdvisorySource
    input_snapshot: dict | None = None
    read_status: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdvisoryGenerateResponse(BaseModel):
    id: uuid.UUID
    farmer_id: uuid.UUID
    crop_block_id: uuid.UUID | None = None
    priority: AdvisoryPriority
    message: str
    recommended_actions: list[str] = []
    reasoning_summary: str | None = None
    disclaimer: str | None = None
    generated_by: AdvisorySource
    input_snapshot: dict | None = None
    read_status: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
