import enum
from sqlalchemy import text, String, Boolean, ForeignKey, Enum as SAEnum, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.base import Base


class AdvisoryPriority(str, enum.Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AdvisorySource(str, enum.Enum):
    GEMINI = "gemini"
    RULE_FALLBACK = "rule_fallback"


class Advisory(Base):
    __tablename__ = "advisories"
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
    crop_block_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("core.crop_blocks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    priority: Mapped[AdvisoryPriority] = mapped_column(
        SAEnum(AdvisoryPriority, name="advisorypriority", schema="logs", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    generated_by: Mapped[AdvisorySource] = mapped_column(
        SAEnum(AdvisorySource, name="advisorysource", schema="logs", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    input_snapshot: Mapped[object] = mapped_column(JSONB, nullable=True)
    read_status: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    farmer: Mapped["FarmerProfile"] = relationship("FarmerProfile", back_populates="advisories")
    crop_block: Mapped["CropBlock"] = relationship("CropBlock", back_populates="advisories")
    feedbacks: Mapped[list["Feedback"]] = relationship(
        "Feedback", back_populates="advisory", cascade="all, delete-orphan"
    )
