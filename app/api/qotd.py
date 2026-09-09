from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.qotd import (
    QotDResponse,
    QotDSubmitRequest,
    QotDSubmitResponse,
)
from app.services.qotd_service import (
    get_streak_multiplier,
    get_today_question,
    get_today_utc,
    get_user_attempt,
    get_or_create_streak,
    submit_qotd,
)


router = APIRouter(
    prefix="/api/v1/qotd",
    tags=["Question of the Day"],
)


@router.get(
    "",
    response_model=QotDResponse,
)
def get_qotd(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = get_today_utc()

    question = get_today_question(db)

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Question of the Day is available",
        )

    attempt = get_user_attempt(
        db,
        current_user.id,
        today,
    )

    streak = get_or_create_streak(
        db,
        current_user.id,
    )

    if attempt is not None:
        multiplier = attempt.multiplier
    else:
        multiplier = get_streak_multiplier(
            max(streak.current_streak, 0)
        )

    return QotDResponse(
        question_id=str(question.id),
        date=today,
        type=question.type,
        difficulty=question.difficulty,
        content=question.content,
        points=question.points,
        streak=streak.current_streak,
        multiplier=multiplier,
    )


@router.post(
    "/submit",
    response_model=QotDSubmitResponse,
)
def submit_question_of_the_day(
    data: QotDSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = get_today_utc()

    question = get_today_question(db)

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Question of the Day is available",
        )

    existing_attempt = get_user_attempt(
        db,
        current_user.id,
        today,
    )

    if existing_attempt is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already attempted today's Question of the Day",
        )

    try:
        attempt = submit_qotd(
            db,
            current_user.id,
            question,
            data.answer,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    streak = get_or_create_streak(
        db,
        current_user.id,
    )

    return QotDSubmitResponse(
        question_id=str(question.id),
        is_correct=attempt.is_correct,
        base_points=attempt.base_points,
        multiplier=attempt.multiplier,
        points_earned=attempt.points_earned,
        current_streak=streak.current_streak,
        longest_streak=streak.longest_streak,
        explanation=question.explanation,
        correct_answer=question.correct_answer,
        submitted_at=attempt.submitted_at,
    )