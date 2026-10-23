import enum
from datetime import date
from sqlalchemy import text, String, Integer, Numeric, Date, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.base import Base


class BlockStatus(str, enum.Enum):
    ACTIVE = "active"
    REMOVED = "removed"
    REPLANTED = "replanted"


class CropBlock(Base):
    __tablename__ = "crop_blocks"
    __table_args__ = {"schema": "core"}

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    farm_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("core.farms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    block_name: Mapped[str] = mapped_column(String, nullable=False)
    variety: Mapped[str | None] = mapped_column(String, nullable=True)
    planting_date: Mapped[date] = mapped_column(Date, nullable=False)
    number_of_trees: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    spacing_meters: Mapped[object] = mapped_column(Numeric, nullable=True)
    status: Mapped[BlockStatus] = mapped_column(
        SAEnum(BlockStatus, name="blockstatus", schema="core", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        server_default=BlockStatus.ACTIVE.value,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    farm: Mapped["Farm"] = relationship("Farm", back_populates="crop_blocks")
    activities: Mapped[list["FarmActivity"]] = relationship(
        "FarmActivity", back_populates="crop_block", cascade="all, delete-orphan"
    )
    disease_detections: Mapped[list["DiseaseDetection"]] = relationship(
        "DiseaseDetection", back_populates="crop_block", cascade="all, delete-orphan"
    )
    advisories: Mapped[list["Advisory"]] = relationship(
        "Advisory", back_populates="crop_block"
    )
    feedbacks: Mapped[list["Feedback"]] = relationship(
        "Feedback", back_populates="crop_block"
    )

    @property
    def age_years(self) -> float:
        """Derived property: tree age in years at query time (age is never stored directly)."""
        if not self.planting_date:
            return 0.0
        delta = date.today() - self.planting_date
        return round(delta.days / 365.25, 2)
