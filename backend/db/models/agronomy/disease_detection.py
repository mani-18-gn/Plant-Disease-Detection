from sqlalchemy import text, String, Numeric, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.base import Base


class DiseaseDetection(Base):
    __tablename__ = "disease_detections"
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
    image_path: Mapped[str] = mapped_column(String, nullable=False)
    predicted_disease: Mapped[str] = mapped_column(String, nullable=False)
    cnn_confidence: Mapped[object] = mapped_column(Numeric, nullable=False)
    posterior_probability: Mapped[object] = mapped_column(Numeric, nullable=True)
    validated: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    detected_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    crop_block: Mapped["CropBlock"] = relationship("CropBlock", back_populates="disease_detections")
