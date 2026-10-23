from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import text, String, ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.db.base import Base

if TYPE_CHECKING:
    from backend.db.models.core.user import User
    from backend.db.models.core.farm import Farm
    from backend.db.models.logs.advisory import Advisory
    from backend.db.models.logs.notification import Notification
    from backend.db.models.logs.feedback import Feedback


class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"
    __table_args__ = {"schema": "core"}

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("core.users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    village: Mapped[str | None] = mapped_column(String, nullable=True)
    taluk: Mapped[str | None] = mapped_column(String, nullable=True)
    district: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    state: Mapped[str | None] = mapped_column(String, nullable=True)
    pincode: Mapped[str | None] = mapped_column(String, nullable=True)
    preferred_language: Mapped[str | None] = mapped_column(String, nullable=True)
    preferred_mandi: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    user: Mapped["User"] = relationship("User", back_populates="farmer_profile")
    farms: Mapped[list["Farm"]] = relationship(
        "Farm", back_populates="farmer", cascade="all, delete-orphan"
    )
    advisories: Mapped[list["Advisory"]] = relationship(
        "Advisory", back_populates="farmer", cascade="all, delete-orphan"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="farmer", cascade="all, delete-orphan"
    )
    feedbacks: Mapped[list["Feedback"]] = relationship(
        "Feedback", back_populates="farmer", cascade="all, delete-orphan"
    )
