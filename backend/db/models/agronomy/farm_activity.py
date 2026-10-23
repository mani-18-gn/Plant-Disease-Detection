from datetime import date, datetime
from typing import TYPE_CHECKING
import enum
from sqlalchemy import text, String, Numeric, Date, ForeignKey, Enum as SAEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.base import Base

if TYPE_CHECKING:
    from backend.db.models.core.crop_block import CropBlock


class ActivityType(str, enum.Enum):
    PLANTING = "planting"
    FERTILIZER = "fertilizer"
    SPRAYING = "spraying"
    IRRIGATION = "irrigation"
    PRUNING = "pruning"
    WEEDING = "weeding"
    HARVESTING = "harvesting"
    SOIL_TEST = "soil_test"
    OTHER = "other"


class LoggedVia(str, enum.Enum):
    APP = "app"
    SMS = "sms"
    AUTO = "auto"


class FarmActivity(Base):
    __tablename__ = "farm_activities"
    __table_args__ = {"schema": "agronomy"}

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    crop_block_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("core.crop_blocks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    activity_type: Mapped[ActivityType] = mapped_column(
        SAEnum(ActivityType, name="activitytype", schema="agronomy", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True,
    )
    activity_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    product_used: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    quantity: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    quantity_unit: Mapped[str | None] = mapped_column(String, nullable=True)
    cost: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    performed_by: Mapped[str | None] = mapped_column(String, nullable=True)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    logged_via: Mapped[LoggedVia] = mapped_column(
        SAEnum(LoggedVia, name="loggedvia", schema="agronomy", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        server_default=LoggedVia.APP.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    crop_block: Mapped["CropBlock"] = relationship("CropBlock", back_populates="activities")
