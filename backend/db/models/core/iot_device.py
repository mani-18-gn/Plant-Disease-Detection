from sqlalchemy import text, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.base import Base


class IoTDevice(Base):
    __tablename__ = "iot_devices"
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
    device_token: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    device_type: Mapped[str | None] = mapped_column(String, nullable=True)
    last_seen_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=True)

    farm: Mapped["Farm"] = relationship("Farm", back_populates="iot_devices")
    soil_readings: Mapped[list["SoilSensorReading"]] = relationship(
        "SoilSensorReading", back_populates="device", cascade="all, delete-orphan"
    )
