
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.game_stage import GameStage
from app.models.user_progress import UserProgress
from app.models.user_score import UserScore


XP_THRESHOLDS = [100, 300, 600, 1000, 2000, 5000, 10000]


def calculate_player_level(xp: int) -> int:
    level = 1

    for threshold in XP_THRESHOLDS:
        if xp >= threshold:
            level += 1
        else:
            break

    return level


def calculate_correctness(is_correct: bool) -> float:
    return 60.0 if is_correct else 0.0


def calculate_time_bonus(
    time_taken: int,
    time_limit: int | None,
) -> float:
    if time_limit is None or time_limit <= 0:
        return 20.0

    if time_taken <= 0:
        return 20.0

    if time_taken >= time_limit:
        return 0.0

    remaining_ratio = (
        time_limit - time_taken
    ) / time_limit

    return round(
        remaining_ratio * 20.0,
        2,
    )


def calculate_efficiency(
    operations_used: int,
    optimal_operations: int | None,
) -> float:
    if optimal_operations is None:
        return 10.0

    if optimal_operations <= 0:
        return 10.0

    if operations_used <= 0:
        return 0.0

    if operations_used <= optimal_operations:
        return 10.0

    ratio = optimal_operations / operations_used

    return round(
        min(ratio, 1.0) * 10.0,
        2,
    )


def calculate_no_hint_score(
    hints_used: int,
) -> float:
    return 10.0 if hints_used == 0 else 0.0


def calculate_stage_score(
    is_correct: bool,
    time_taken: int,
    time_limit: int | None,
    hints_used: int,
    operations_used: int,
    optimal_operations: int | None,
) -> dict:
    correctness = calculate_correctness(
        is_correct
    )

    time_bonus = calculate_time_bonus(
        time_taken,
        time_limit,
    )

    efficiency = calculate_efficiency(
        operations_used,
        optimal_operations,
    )

    no_hint = calculate_no_hint_score(
        hints_used
    )

    total = round(
        correctness
        + time_bonus
        + efficiency
        + no_hint
    )

    total = max(
        0,
        min(total, 100),
    )

    return {
        "correctness": correctness,
        "time_bonus": time_bonus,
        "efficiency": efficiency,
        "no_hint": no_hint,
        "total_score": total,
    }


def get_or_create_user_score(
    db: Session,
    user_id,
) -> UserScore:
    user_score = db.scalar(
        select(UserScore).where(
            UserScore.user_id == user_id
        )
    )

    if user_score is None:
        user_score = UserScore(
            user_id=user_id,
            total_score=0,
            daily_score=0,
            weekly_score=0,
            monthly_score=0,
            xp=0,
            player_level=1,
        )

        db.add(user_score)
        db.flush()

    return user_score


def update_user_score(
    db: Session,
    user_id,
    score_value: int,
) -> UserScore:
    user_score = get_or_create_user_score(
        db,
        user_id,
    )

    user_score.total_score += score_value
    user_score.daily_score += score_value
    user_score.weekly_score += score_value
    user_score.monthly_score += score_value

    return user_score


def add_xp(
    db: Session,
    user_id,
    xp_amount: int,
) -> UserScore:
    user_score = get_or_create_user_score(
        db,
        user_id,
    )

    user_score.xp += xp_amount

    user_score.player_level = calculate_player_level(
        user_score.xp
    )

    return user_score


def has_completed_level(
    db: Session,
    user_id,
    level_id,
) -> bool:
    stages = db.scalars(
        select(GameStage).where(
            GameStage.level_id == level_id
        )
    ).all()

    if not stages:
        return False

    completed_stages = db.scalars(
        select(UserProgress).where(
            UserProgress.user_id == user_id,
            UserProgress.level_id == level_id,
            UserProgress.status == "completed",
        )
    ).all()

    return len(completed_stages) >= len(stages)


def process_stage_score(
    db: Session,
    user_id,
    progress: UserProgress,
    stage: GameStage,
    is_correct: bool,
    time_taken: int,
    operations_used: int,
) -> tuple[dict, int, UserScore]:

    previous_status = progress.status

    level_was_completed = has_completed_level(
        db,
        user_id,
        stage.level_id,
    )

    optimal_operations = None

    if stage.challenge_data:
        optimal_operations = stage.challenge_data.get(
            "optimal_operations"
        )

    breakdown = calculate_stage_score(
        is_correct=is_correct,
        time_taken=time_taken,
        time_limit=stage.time_limit,
        hints_used=progress.hints_used,
        operations_used=operations_used,
        optimal_operations=optimal_operations,
    )

    score_value = breakdown["total_score"]

    progress.score = score_value
    progress.time_taken = time_taken

    if score_value > (
        progress.highest_score or 0
    ):
        progress.highest_score = score_value

    is_passing = (
        is_correct
        and score_value >= stage.passing_score
    )

    if is_passing:
        progress.status = "completed"
        progress.completed_at = datetime.now(
            timezone.utc
        )
    else:
        progress.status = "failed"

    user_score = get_or_create_user_score(
        db,
        user_id,
    )

    if is_passing:
        user_score = update_user_score(
            db,
            user_id,
            score_value,
        )

    xp_earned = 0

    stage_completed_first_time = (
        progress.status == "completed"
        and previous_status != "completed"
    )

    if stage_completed_first_time:
        xp_earned += 5

        db.flush()

        level_is_completed = has_completed_level(
            db,
            user_id,
            stage.level_id,
        )

        if (
            level_is_completed
            and not level_was_completed
        ):
            xp_earned += 50

    if xp_earned > 0:
        user_score.xp += xp_earned

        user_score.player_level = (
            calculate_player_level(
                user_score.xp
            )
        )

    db.commit()

    db.refresh(progress)
    db.refresh(user_score)

    return (
        breakdown,
        xp_earned,
        user_score,
    )

