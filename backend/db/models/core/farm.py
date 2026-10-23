from datetime import datetime
from typing import TYPE_CHECKING
import enum
from sqlalchemy import text, String, ForeignKey, Numeric, Enum as SAEnum
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.base import Base

if TYPE_CHECKING:
    from backend.db.models.core.farmer_profile import FarmerProfile
    from backend.db.models.core.crop_block import CropBlock
    from backend.db.models.core.iot_device import IoTDevice
    from backend.db.models.env.weather_reading import WeatherReading


class IrrigationType(str, enum.Enum):
    DRIP = "drip"
    FLOOD = "flood"
    SPRINKLER = "sprinkler"
    RAINFED = "rainfed"


class Farm(Base):
    __tablename__ = "farms"
    __table_args__ = {"schema": "core"}

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
    farm_name: Mapped[str] = mapped_column(String, nullable=False)
    latitude: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    total_area_acres: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    soil_type: Mapped[str | None] = mapped_column(String, nullable=True)
    irrigation_type: Mapped[IrrigationType | None] = mapped_column(
        SAEnum(IrrigationType, name="irrigationtype", schema="core", values_callable=lambda obj: [e.value for e in obj]),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    farmer: Mapped["FarmerProfile"] = relationship("FarmerProfile", back_populates="farms")
    crop_blocks: Mapped[list["CropBlock"]] = relationship(
        "CropBlock", back_populates="farm", cascade="all, delete-orphan"
    )
    iot_devices: Mapped[list["IoTDevice"]] = relationship(
        "IoTDevice", back_populates="farm", cascade="all, delete-orphan"
    )
    weather_readings: Mapped[list["WeatherReading"]] = relationship(
        "WeatherReading", back_populates="farm", cascade="all, delete-orphan"
    )
