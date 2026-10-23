import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.db.models.core.user import User
from backend.db.models.core.farmer_profile import FarmerProfile
from backend.db.models.logs.advisory import Advisory
from backend.auth.jwt_handler import get_current_user
from backend.core.router import _verify_crop_block_ownership
from backend.schemas.learning import (
    FeedbackSubmitRequest,
    FeedbackSubmissionResponse,
    LearningScoreResponse,
    FeedbackSummaryResponse,
)
from backend.agents.learning.feedback_store import (
    record_feedback,
    get_feedback_summary,
    list_feedback_for_farmer,
)
from backend.agents.learning.q_learning import (
    normalize_reward,
    extract_state_key,
    extract_action_key,
    get_learning_score,
)

router = APIRouter(prefix="/agents/learning", tags=["Learning Agent"])


@router.post("/feedback", response_model=FeedbackSubmissionResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    payload: FeedbackSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Learning Agent Feedback Endpoint (Major_Final_!.md §4.4.6 / §4.5.3.6):
    Captures farmer rating (1-5), normalizes reward r in [-1.0, +1.0], and performs
    Contextual Bandit reinforcement value updating for the corresponding (s, a) cell.
    """
    farmer_profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == str(current_user.id)).first()
    if not farmer_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found")

    # 1. Record in logs.feedback
    feedback = record_feedback(
        db=db,
        advisory_id=str(payload.advisory_id),
        farmer_id=str(farmer_profile.id),
        rating=payload.rating,
        outcome_notes=payload.outcome_notes,
    )

    # 2. Extract State and Action Keys from parent advisory
    advisory = db.query(Advisory).filter(Advisory.id == str(payload.advisory_id)).first()
    if not advisory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent advisory not found")
    snapshot = advisory.input_snapshot if isinstance(advisory.input_snapshot, dict) else {}
    state_k = extract_state_key(snapshot)
    priority_val = advisory.priority.value if hasattr(advisory.priority, "value") else str(advisory.priority)
    action_k = extract_action_key(priority_val, snapshot.get("recommended_actions", []))

    # 3. Query Cell-Specific Learning Score
    score_data = get_learning_score(db, state_k, action_k)

    return FeedbackSubmissionResponse(
        feedback_id=uuid.UUID(str(feedback.id)),
        advisory_id=uuid.UUID(str(feedback.advisory_id)),
        crop_block_id=uuid.UUID(str(feedback.crop_block_id)) if feedback.crop_block_id else None,
        farmer_id=uuid.UUID(str(feedback.farmer_id)),
        rating=feedback.rating,
        normalized_reward=normalize_reward(feedback.rating),
        state_key=state_k,
        action_key=action_k,
        cell_observations=score_data["observations"],
        updated_q_value=score_data["q_value"],
        learning_score=score_data["learning_score"],
        status=score_data["status"],
        created_at=feedback.created_at,
    )


@router.get("/summary/crop_block/{crop_block_id}", response_model=FeedbackSummaryResponse)
def get_crop_block_feedback_summary(
    crop_block_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves aggregated feedback metrics for a specific crop block."""
    _verify_crop_block_ownership(db, str(crop_block_id), str(current_user.id))
    summary = get_feedback_summary(db, crop_block_id=str(crop_block_id))
    return FeedbackSummaryResponse(
        crop_block_id=crop_block_id,
        total_feedback_count=summary["total_feedback_count"],
        average_rating=summary["average_rating"],
        rating_distribution=summary["rating_distribution"],
    )


@router.get("/score", response_model=LearningScoreResponse)
def get_q_learning_score(
    state_key: str = Query(..., description="Discrete state key, e.g. 'koleroga:urgent:rising'"),
    action_key: str = Query(..., description="Discrete action key, e.g. 'urgent:fungicide_spray'"),
    db: Session = Depends(get_db),
):
    """
    Queries the learned confidence score for a given state-action context cell.
    Returns 50.0 baseline if cell observations < MIN_CELL_OBSERVATIONS (3).
    """
    res = get_learning_score(db, state_key=state_key, action_key=action_key)
    return LearningScoreResponse(
        state_key=res["state_key"],
        action_key=res["action_key"],
        q_value=res["q_value"],
        learning_score=res["learning_score"],
        observations=res["observations"],
        required_observations=res["required_observations"],
        status=res["status"],
    )
