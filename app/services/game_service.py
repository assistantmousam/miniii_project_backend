from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.game_level import GameLevel
from app.models.game_stage import GameStage
from app.models.user_progress import UserProgress


def get_all_levels(
    db: Session,
) -> list[GameLevel]:

    return db.scalars(
        select(GameLevel)
        .where(GameLevel.is_active.is_(True))
        .order_by(GameLevel.order_index)
    ).all()


def get_level_by_id(
    db: Session,
    level_id,
) -> GameLevel | None:

    return db.scalar(
        select(GameLevel).where(
            GameLevel.id == level_id,
            GameLevel.is_active.is_(True),
        )
    )


def get_stage_by_id(
    db: Session,
    stage_id,
) -> GameStage | None:

    return db.scalar(
        select(GameStage).where(
            GameStage.id == stage_id
        )
    )


def get_user_stage_progress(
    db: Session,
    user_id,
    stage_id,
) -> UserProgress | None:

    return db.scalar(
        select(UserProgress).where(
            UserProgress.user_id == user_id,
            UserProgress.stage_id == stage_id,
        )
    )


def is_level_unlocked(
    db: Session,
    user_id,
    level: GameLevel,
) -> bool:

    # Level 1 is always unlocked.
    if level.level_number == 1:
        return True

    previous_level = db.scalar(
        select(GameLevel).where(
            GameLevel.level_number == level.level_number - 1
        )
    )

    if previous_level is None:
        return False

    stages = db.scalars(
        select(GameStage).where(
            GameStage.level_id == previous_level.id
        )
    ).all()

    if not stages:
        return False

    completed_count = db.scalar(
        select(UserProgress.id).where(
            UserProgress.user_id == user_id,
            UserProgress.level_id == previous_level.id,
            UserProgress.status == "completed",
        ).limit(1)
    )

    return completed_count is not None


def is_stage_unlocked(
    db: Session,
    user_id,
    stage: GameStage,
) -> bool:

    level = get_level_by_id(
        db,
        stage.level_id,
    )

    if level is None:
        return False

    if not is_level_unlocked(
        db,
        user_id,
        level,
    ):
        return False

    # First stage is unlocked when the level is unlocked.
    if stage.stage_number == 1:
        return True

    previous_stage = db.scalar(
        select(GameStage).where(
            GameStage.level_id == stage.level_id,
            GameStage.stage_number == stage.stage_number - 1,
        )
    )

    if previous_stage is None:
        return False

    previous_progress = get_user_stage_progress(
        db,
        user_id,
        previous_stage.id,
    )

    if previous_progress is None:
        return False

    return (
        previous_progress.status == "completed"
        and previous_progress.highest_score >= 60
    )


def start_stage(
    db: Session,
    user_id,
    stage: GameStage,
) -> UserProgress:

    progress = get_user_stage_progress(
        db,
        user_id,
        stage.id,
    )

    if progress is None:
        progress = UserProgress(
            user_id=user_id,
            level_id=stage.level_id,
            stage_id=stage.id,
            status="in_progress",
            score=0,
            highest_score=0,
            attempts=0,
            hints_used=0,
            time_taken=0,
        )

        db.add(progress)

    else:
        progress.status = "in_progress"

    db.commit()
    db.refresh(progress)

    return progress


def submit_stage(
    db: Session,
    progress: UserProgress,
    stage: GameStage,
    answer: dict,
    time_taken: int,
    hints_used: int,
) -> tuple[int, bool]:

    progress.attempts += 1
    progress.time_taken = time_taken
    progress.hints_used = hints_used

    # Basic answer validation.
    expected_answer = stage.challenge_data.get(
        "correct_answer"
    )

    is_correct = answer == expected_answer

    if is_correct:
        score = 100

        # 10 points penalty for each hint.
        score -= hints_used * 10

        score = max(score, 0)

        progress.score = score

        if score > progress.highest_score:
            progress.highest_score = score

        if score >= stage.passing_score:
            progress.status = "completed"

    else:
        score = 0
        progress.score = 0
        progress.status = "failed"

    db.commit()
    db.refresh(progress)

    return score, is_correct