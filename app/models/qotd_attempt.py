import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Float
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class QotDAttempt(Base):
    __tablename__ = "qotd_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id"),
        nullable=False,
        index=True,
    )

    attempt_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    answer: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    base_points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    multiplier: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )

    points_earned: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="qotd_attempts",
    )

    question = relationship(
        "Question",
    )