from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.question import Question
from app.models.qotd_attempt import QotDAttempt
from app.models.streak import Streak
from app.models.user_score import UserScore


def get_today_utc() -> date:
    return datetime.now(timezone.utc).date()


def get_or_create_streak(
    db: Session,
    user_id,
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


def get_streak_multiplier(streak: int) -> float:
    if streak >= 30:
        return 3.0

    if streak >= 7:
        return 2.0

    if streak >= 3:
        return 1.5

    return 1.0


def update_streak(
    db: Session,
    user_id,
    today: date,
) -> Streak:

    streak = get_or_create_streak(db, user_id)

    if streak.last_answer_date == today:
        return streak

    if (
        streak.last_answer_date is not None
        and streak.last_answer_date == today - timedelta(days=1)
    ):
        streak.current_streak += 1
    else:
        streak.current_streak = 1

    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak

    streak.last_answer_date = today

    db.flush()

    return streak


def get_today_question(
    db: Session,
) -> Question | None:

    today = get_today_utc()

    question = db.scalar(
        select(Question)
        .where(
            Question.used_date == today
        )
    )

    if question is not None:
        return question

    question = db.scalar(
        select(Question)
        .where(
            Question.is_used.is_(False)
        )
        .order_by(Question.created_at if hasattr(Question, "created_at") else Question.id)
    )

    if question is None:
        return None

    question.is_used = True
    question.used_date = today

    db.commit()
    db.refresh(question)

    return question


def get_user_attempt(
    db: Session,
    user_id,
    today: date,
) -> QotDAttempt | None:

    return db.scalar(
        select(QotDAttempt).where(
            QotDAttempt.user_id == user_id,
            QotDAttempt.attempt_date == today,
        )
    )


def submit_qotd(
    db: Session,
    user_id,
    question: Question,
    answer: dict,
) -> QotDAttempt:

    today = get_today_utc()

    existing_attempt = get_user_attempt(
        db,
        user_id,
        today,
    )

    if existing_attempt is not None:
        raise ValueError(
            "You have already attempted today's Question of the Day"
        )

    is_correct = answer == question.correct_answer

    streak = update_streak(
        db,
        user_id,
        today,
    )

    multiplier = get_streak_multiplier(
        streak.current_streak
    )

    base_points = question.points

    points_earned = (
        round(base_points * multiplier)
        if is_correct
        else 0
    )

    attempt = QotDAttempt(
        user_id=user_id,
        question_id=question.id,
        attempt_date=today,
        answer=answer,
        is_correct=is_correct,
        base_points=base_points,
        multiplier=multiplier,
        points_earned=points_earned,
        submitted_at=datetime.now(timezone.utc),
    )

    db.add(attempt)

    if is_correct:
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

        user_score.total_score += points_earned
        user_score.daily_score += points_earned
        user_score.weekly_score += points_earned
        user_score.monthly_score += points_earned

        user_score.xp += points_earned

    db.commit()
    db.refresh(attempt)

    return attempt