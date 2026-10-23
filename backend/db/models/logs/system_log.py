from datetime import datetime
import enum
from sqlalchemy import text, String, Text, Enum as SAEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from backend.db.base import Base


class LogLevel(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class SystemLog(Base):
    __tablename__ = "system_logs"
    __table_args__ = {"schema": "logs"}

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    service: Mapped[str] = mapped_column(String, nullable=False, index=True)
    level: Mapped[LogLevel] = mapped_column(
        SAEnum(LogLevel, name="loglevel", schema="logs", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
