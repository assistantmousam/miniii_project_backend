import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class GameLevel(Base):
    __tablename__ = "game_levels"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    level_number: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    topic: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    difficulty: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    unlock_requires: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("game_levels.id"),
        nullable=True,
    )

    icon_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    stages = relationship(
        "GameStage",
        back_populates="level",
        cascade="all, delete-orphan",
    )

    prerequisite = relationship(
        "GameLevel",
        remote_side=[id],
        back_populates="unlocked_levels",
    )

    unlocked_levels = relationship(
        "GameLevel",
        back_populates="prerequisite",
    )