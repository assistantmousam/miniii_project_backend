import uuid

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserScore(Base):
    __tablename__ = "user_scores"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        primary_key=True,
    )

    total_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    daily_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    weekly_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    monthly_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    xp: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    player_level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="score",
    )