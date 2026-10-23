from datetime import date
from sqlalchemy import text, String, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from backend.db.base import Base


class MarketPrice(Base):
    __tablename__ = "market_prices"
    __table_args__ = {"schema": "market"}

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    mandi_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    commodity: Mapped[str] = mapped_column(String, nullable=False, index=True)
    price_per_kg: Mapped[object] = mapped_column(Numeric, nullable=False)
    price_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
