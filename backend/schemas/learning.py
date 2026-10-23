import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class FeedbackSubmitRequest(BaseModel):
    advisory_id: uuid.UUID
    rating: int = Field(..., ge=1, le=5, description="Farmer satisfaction rating from 1 (very poor) to 5 (excellent)")
    outcome_notes: str | None = Field(None, description="Optional agronomic observations or crop response notes")


class FeedbackSubmissionResponse(BaseModel):
    feedback_id: uuid.UUID
    advisory_id: uuid.UUID
    crop_block_id: uuid.UUID | None = None
    farmer_id: uuid.UUID
    rating: int
    normalized_reward: float
    state_key: str
    action_key: str
    cell_observations: int
    updated_q_value: float
    learning_score: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LearningScoreResponse(BaseModel):
    state_key: str
    action_key: str
    q_value: float
    learning_score: float
    observations: int
    required_observations: int
    status: str  # "learned_active" | "insufficient_data_using_baseline"


class FeedbackSummaryResponse(BaseModel):
    crop_block_id: uuid.UUID | None = None
    total_feedback_count: int
    average_rating: float
    rating_distribution: dict[str, int]
