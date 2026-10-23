from datetime import datetime
from typing import TYPE_CHECKING
import enum
from sqlalchemy import text, ForeignKey, Text, Enum as SAEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.base import Base

if TYPE_CHECKING:
    from backend.db.models.core.farmer_profile import FarmerProfile


class NotificationChannel(str, enum.Enum):
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationStatus(str, enum.Enum):
    SENT = "sent"
    FAILED = "failed"
    PENDING = "pending"


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = {"schema": "logs"}

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    farmer_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("core.farmer_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        SAEnum(NotificationChannel, name="notificationchannel", schema="logs", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        SAEnum(NotificationStatus, name="notificationstatus", schema="logs", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        server_default=NotificationStatus.PENDING.value,
    )
    # sent_at is nullable: pending notifications have not been sent yet
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    farmer: Mapped["FarmerProfile"] = relationship("FarmerProfile", back_populates="notifications")
