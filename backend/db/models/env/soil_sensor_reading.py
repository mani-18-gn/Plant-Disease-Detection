from sqlalchemy import text, Numeric, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.base import Base


class SoilSensorReading(Base):
    __tablename__ = "soil_sensor_readings"
    __table_args__ = {"schema": "env"}

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    device_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("core.iot_devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    moisture_pct: Mapped[object] = mapped_column(Numeric, nullable=False)
    recorded_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    device: Mapped["IoTDevice"] = relationship("IoTDevice", back_populates="soil_readings")
