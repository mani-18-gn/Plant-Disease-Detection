import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.db.models.logs.notification import (
    Notification,
    NotificationChannel,
    NotificationStatus,
)
from backend.db.models.logs.advisory import Advisory, AdvisoryPriority
from backend.db.models.logs.system_log import LogLevel
from backend.agents.notifying.monitoring import log_system_event

logger = logging.getLogger(__name__)


def send_notification(
    db: Session,
    farmer_id: str,
    channel: NotificationChannel,
    content: str,
    status_override: NotificationStatus | None = None,
) -> Notification:
    """
    Creates and records a notification record in logs.notifications.
    - IN_APP: Marked 'sent' with current sent_at timestamp.
    - SMS: Marked 'pending' (sent_at=None) with mock gateway log note.
    - PUSH: Marked 'pending' (ready for mobile token delivery).
    """
    if status_override:
        final_status = status_override
    elif channel == NotificationChannel.IN_APP:
        final_status = NotificationStatus.SENT
    else:
        final_status = NotificationStatus.PENDING

    sent_time = datetime.now(timezone.utc) if final_status == NotificationStatus.SENT else None

    notification = Notification(
        farmer_id=str(farmer_id),
        channel=channel,
        content=content,
        status=final_status,
        sent_at=sent_time,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    if channel == NotificationChannel.SMS:
        logger.info(
            f"[SMS MOCK GATEWAY] SMS dispatch queued for farmer {farmer_id}: '{content[:80]}...' "
            "(Status: PENDING - Telephony provider integration pending)"
        )
        log_system_event(
            db,
            service="notifying",
            level=LogLevel.INFO,
            message=f"SMS queued for farmer {farmer_id} (Mock gateway)",
        )

    return notification


def dispatch_advisory_notifications(db: Session, advisory: Advisory) -> list[Notification]:
    """
    Table 4.5 Priority Matrix Notification Dispatcher:
    - URGENT: Dispatches IN_APP (sent) and SMS (pending mock queue).
    - HIGH:   Dispatches IN_APP (sent).
    - MEDIUM: Dispatches IN_APP (sent).
    - LOW:    No notification created (dashboard update only).
    """
    p = advisory.priority
    if isinstance(p, str):
        priority_val = p.lower()
    else:
        priority_val = p.value.lower() if hasattr(p, "value") else str(p).lower()

    farmer_id = str(advisory.farmer_id)
    content = f"[{priority_val.upper()} ADVISORY] {advisory.message}"
    dispatched = []

    if priority_val == "urgent":
        # Table 4.5: Immediate SMS + App notification
        in_app_notif = send_notification(db, farmer_id, NotificationChannel.IN_APP, content)
        sms_notif = send_notification(db, farmer_id, NotificationChannel.SMS, content)
        dispatched.extend([in_app_notif, sms_notif])
    elif priority_val in ["high", "medium"]:
        # Table 4.5: In-app notification
        in_app_notif = send_notification(db, farmer_id, NotificationChannel.IN_APP, content)
        dispatched.append(in_app_notif)
    elif priority_val == "low":
        # Table 4.5: Dashboard update only
        logger.info(f"Advisory {advisory.id} priority is LOW; dashboard update only (no notification queued).")

    return dispatched


def get_notifications_for_farmer(
    db: Session,
    farmer_id: str,
    unread_only: bool = False,
) -> list[Notification]:
    """Retrieves all notifications for a given farmer profile."""
    query = db.query(Notification).filter(Notification.farmer_id == str(farmer_id))
    if unread_only:
        query = query.filter(Notification.status == NotificationStatus.SENT)
    return query.order_by(Notification.sent_at.desc().nullslast()).all()
