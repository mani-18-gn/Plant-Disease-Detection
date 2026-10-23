from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.db.models.core.user import User
from backend.auth.jwt_handler import get_current_user
from backend.schemas.coordinator import SynthesizeRequest, CoordinatorSynthesizeResponse
from backend.agents.coordinator.orchestrator import synthesize_farm_status

router = APIRouter(prefix="/agents/coordinator", tags=["Coordinator Agent"])


@router.post("/synthesize", response_model=CoordinatorSynthesizeResponse, status_code=status.HTTP_200_OK)
def synthesize_decision(
    payload: SynthesizeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Coordinator Agent Synthesis Endpoint (Major_Final_!.md §4.4.7 / §4.5.3.7):
    Orchestrates cross-agent synthesis across Diagnosis (35%), Weather (30%), Market (20%),
    and Learning (15%), computing the composite situation score and delivering unified advisory actions.
    """
    return synthesize_farm_status(
        db=db,
        crop_block_id=str(payload.crop_block_id),
        current_user=current_user,
        detection_id=str(payload.detection_id) if payload.detection_id else None,
    )
