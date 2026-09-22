from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.question import Question
from app.models.qotd_attempt import QotDAttempt
from app.models.streak import Streak
from app.models.user_score import UserScore


# ============================================================
# XP THRESHOLDS
# ============================================================

XP_THRESHOLDS = [
    100,
    300,
    600,
    1000,
    2000,
    5000,
    10000,
]


# ============================================================
# TODAY
# ============================================================

def get_today_utc() -> date:
    return datetime.now(timezone.utc).date()


# ============================================================
# PLAYER LEVEL
# ============================================================

def calculate_level_from_xp(xp: int) -> int:
    level = 1

    for threshold in XP_THRESHOLDS:
        if xp >= threshold:
            level += 1
        else:
            break

    return level


# ============================================================
# STREAK
# ============================================================

def get_or_create_streak(
    db: Session,
    user_id: int,
) -> Streak:

    streak = db.scalar(
        select(Streak).where(
            Streak.user_id == user_id
        )
    )

    if streak is None:
        streak = Streak(
            user_id=user_id,
            current_streak=0,
            longest_streak=0,
            last_answer_date=None,
        )

        db.add(streak)
        db.flush()

    return streak


def get_streak_multiplier(
    streak: int,
) -> float:

    if streak >= 30:
        return 3.0

    if streak >= 7:
        return 2.0

    if streak >= 3:
        return 1.5

    return 1.0


def update_streak(
    db: Session,
    user_id: int,
    today: date,
) -> Streak:

    streak = get_or_create_streak(
        db,
        user_id,
    )

    # Already answered today
    if streak.last_answer_date == today:
        return streak

    # Continue yesterday's streak
    if (
        streak.last_answer_date is not None
        and streak.last_answer_date
        == today - timedelta(days=1)
    ):
        streak.current_streak += 1

    # Start a new streak
    else:
        streak.current_streak = 1

    # Update longest streak
    if (
        streak.current_streak
        > streak.longest_streak
    ):
        streak.longest_streak = (
            streak.current_streak
        )

    streak.last_answer_date = today

    db.flush()

    return streak


# ============================================================
# TODAY'S QUESTION
# ============================================================

def get_today_question(
    db: Session,
) -> Question | None:

    today = get_today_utc()

    # --------------------------------------------------------
    # Check whether today's question already exists
    # --------------------------------------------------------

    existing = db.scalar(
        select(Question).where(
            Question.used_date == today,
            Question.is_qotd_eligible.is_(True),
        )
    )

    if existing is not None:
        return existing

    # --------------------------------------------------------
    # Select an unused eligible question
    # --------------------------------------------------------

    question = db.scalar(
        select(Question)
        .where(
            Question.used_date.is_(None),
            Question.is_qotd_eligible.is_(True),
        )
        .order_by(func.random())
        .with_for_update(
            skip_locked=True
        )
    )

    # --------------------------------------------------------
    # Fallback: reuse oldest question
    # --------------------------------------------------------

    if question is None:
        question = db.scalar(
            select(Question)
            .where(
                Question.is_qotd_eligible.is_(True)
            )
            .order_by(
                Question.used_date.asc()
            )
            .with_for_update()
        )

    # --------------------------------------------------------
    # No question available
    # --------------------------------------------------------

    if question is None:
        return None

    # --------------------------------------------------------
    # Mark question as today's QOTD
    # --------------------------------------------------------

    question.used_date = today

    # Do not commit here.
    # The submit/API layer controls the transaction.

    db.flush()

    return question


# ============================================================
# GET USER TODAY'S ATTEMPT
# ============================================================

def get_user_attempt(
    db: Session,
    user_id: int,
    today: date,
) -> QotDAttempt | None:

    return db.scalar(
        select(QotDAttempt).where(
            QotDAttempt.user_id == user_id,
            QotDAttempt.attempt_date == today,
        )
    )


# ============================================================
# GET OR CREATE USER SCORE
# ============================================================

def get_or_create_user_score(
    db: Session,
    user_id: int,
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


# ============================================================
# CHECK ANSWER
# ============================================================

def check_answer(
    question: Question,
    answer: str,
) -> bool:

    if answer is None:
        return False

    user_answer = str(answer).strip()

    correct_answer = str(
        question.correct_answer
    ).strip()

    return user_answer == correct_answer


# ============================================================
# SUBMIT QOTD
# ============================================================

def submit_qotd(
    db: Session,
    user_id: int,
    answer: str,
) -> QotDAttempt:

    today = get_today_utc()

    # --------------------------------------------------------
    # Check duplicate attempt FIRST
    # --------------------------------------------------------

    existing_attempt = get_user_attempt(
        db,
        user_id,
        today,
    )

    if existing_attempt is not None:
        raise ValueError(
            "You have already attempted today's "
            "Question of the Day"
        )

    # --------------------------------------------------------
    # Get today's question
    # --------------------------------------------------------

    qotd = get_today_question(db)

    if qotd is None:
        raise ValueError(
            "Today's Question of the Day is not available"
        )

    # --------------------------------------------------------
    # Check answer
    # --------------------------------------------------------

    is_correct = check_answer(
        qotd,
        answer,
    )

    base_points = qotd.points or 0

    points_earned = 0

    multiplier = 1.0

    # --------------------------------------------------------
    # Correct answer
    # --------------------------------------------------------

    if is_correct:

        # Streak changes ONLY on correct answer
        streak = update_streak(
            db,
            user_id,
            today,
        )

        multiplier = get_streak_multiplier(
            streak.current_streak
        )

        points_earned = round(
            base_points * multiplier
        )

    # --------------------------------------------------------
    # Create attempt
    # --------------------------------------------------------

    attempt = QotDAttempt(
        user_id=user_id,
        question_id=qotd.id,
        attempt_date=today,
        answer=answer,
        is_correct=is_correct,
        base_points=base_points,
        multiplier=multiplier,
        points_earned=points_earned,
        submitted_at=datetime.now(timezone.utc),
    )

    db.add(attempt)

    # --------------------------------------------------------
    # Update score and XP ONLY if correct
    # --------------------------------------------------------

    if is_correct:

        user_score = get_or_create_user_score(
            db,
            user_id,
        )

        # Score
        user_score.total_score += points_earned
        user_score.daily_score += points_earned
        user_score.weekly_score += points_earned
        user_score.monthly_score += points_earned

        # XP
        user_score.xp += points_earned

        # Player level
        user_score.player_level = (
            calculate_level_from_xp(
                user_score.xp
            )
        )

    # --------------------------------------------------------
    # Commit
    # --------------------------------------------------------

    db.commit()

    db.refresh(attempt)

    return attempt