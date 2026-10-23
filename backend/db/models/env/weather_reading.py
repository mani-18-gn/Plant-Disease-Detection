from datetime import datetime
from typing import TYPE_CHECKING
import enum
from sqlalchemy import text, String, Numeric, ForeignKey, Enum as SAEnum, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.base import Base

if TYPE_CHECKING:
    from backend.db.models.core.farm import Farm


class WeatherSource(str, enum.Enum):
    API = "api"
    FORECAST = "forecast"
    SYNTHETIC_FALLBACK = "synthetic_fallback"
    HISTORICAL_BACKFILL = "historical_backfill"


class WeatherReading(Base):
    __tablename__ = "weather_readings"
    __table_args__ = (
        # At least one of farm_id or region_key must be set
        CheckConstraint(
            "farm_id IS NOT NULL OR region_key IS NOT NULL",
            name="ck_weather_readings_farm_or_region",
        ),
        {"schema": "env"},
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    farm_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("core.farms.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    # region_key: grid-cell cache key, used instead of or alongside farm_id
    region_key: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    temperature: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    humidity: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    rainfall_mm: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    source: Mapped[WeatherSource] = mapped_column(
        SAEnum(WeatherSource, name="weathersource", schema="env", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    farm: Mapped["Farm"] = relationship("Farm", back_populates="weather_readings")
