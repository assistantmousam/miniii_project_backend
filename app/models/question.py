import uuid
from datetime import date

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    difficulty: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    content: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    correct_answer: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    tags: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
    )

    is_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    used_date: Mapped[date | None] = mapped_column(
        nullable=True,
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )