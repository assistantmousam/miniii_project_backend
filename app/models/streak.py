import uuid
from datetime import date

from sqlalchemy import Date, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Streak(Base):
    __tablename__ = "streaks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        index=True,
    )

    current_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    longest_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    last_answer_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )