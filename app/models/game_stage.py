import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class GameStage(Base):
    __tablename__ = "game_stages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    level_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("game_levels.id"),
        nullable=False,
        index=True,
    )

    stage_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    difficulty: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    challenge_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    challenge_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    time_limit: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    passing_score: Mapped[int] = mapped_column(
        Integer,
        default=60,
        nullable=False,
    )

    max_hints: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
    )

    solution_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    level = relationship(
        "GameLevel",
        back_populates="stages",
    )

    progress = relationship(
        "UserProgress",
        back_populates="stage",
    )