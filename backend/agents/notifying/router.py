import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.db.models.core.user import User
from backend.db.models.core.farmer_profile import FarmerProfile
from backend.auth.jwt_handler import get_current_user
from backend.schemas.notifying import (
    NotificationSendRequest,
    NotificationResponse,
    HealthCheckResponse,
)
from backend.agents.notifying.notifications import (
    send_notification,
    get_notifications_for_farmer,
)
from backend.agents.notifying.monitoring import get_system_health

router = APIRouter(prefix="/agents/notifying", tags=["Notifying / Monitoring Agent"])


@router.post("/send", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def dispatch_notification_endpoint(
    payload: NotificationSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Notifying Agent: Explicitly queues/sends a notification to a farmer.
    Enforces that callers can only send notifications to their own profile (or admin).
    """
    target_profile = db.query(FarmerProfile).filter(FarmerProfile.id == str(payload.farmer_id)).first()
    if not target_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target farmer profile not found")

    if str(target_profile.user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to send notifications for this farmer")

    notification = send_notification(
        db=db,
        farmer_id=str(payload.farmer_id),
        channel=payload.channel,
        content=payload.content,
    )
    return notification


@router.get("/health", response_model=HealthCheckResponse, status_code=status.HTTP_200_OK)
def get_health_check(db: Session = Depends(get_db)):
    """
    Monitoring Agent Health Check Endpoint (Major_Final_!.md §5.1):
    Public unauthenticated health probe reporting PostgreSQL latency, external API reachability,
    and system log metrics.
    """
    return get_system_health(db)


@router.get("/{farmer_id}", response_model=list[NotificationResponse])
def list_farmer_notifications(
    farmer_id: uuid.UUID,
    unread_only: bool = Query(False, description="Filter for unread/sent notifications only"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Notifying Agent: Retrieves notification history for an authenticated farmer.
    """
    profile = db.query(FarmerProfile).filter(FarmerProfile.id == str(farmer_id)).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found")

    if str(profile.user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to farmer notifications")

    return get_notifications_for_farmer(db, str(farmer_id), unread_only=unread_only)
