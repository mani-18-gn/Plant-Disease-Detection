from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import text, Integer, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.base import Base

if TYPE_CHECKING:
    from backend.db.models.logs.advisory import Advisory
    from backend.db.models.core.farmer_profile import FarmerProfile
    from backend.db.models.core.crop_block import CropBlock


class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = {"schema": "logs"}

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    advisory_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("logs.advisories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    farmer_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("core.farmer_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Extra column: nullable FK to crop_blocks — shortcut for Learning Agent
    # to query feedback per block without joining through advisories.
    crop_block_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("core.crop_blocks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    outcome_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    advisory: Mapped["Advisory"] = relationship("Advisory", back_populates="feedbacks")
    farmer: Mapped["FarmerProfile"] = relationship("FarmerProfile", back_populates="feedbacks")
    crop_block: Mapped["CropBlock"] = relationship("CropBlock", back_populates="feedbacks")
