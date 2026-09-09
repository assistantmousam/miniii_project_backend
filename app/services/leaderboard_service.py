from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_score import UserScore


VALID_PERIODS = {
    "daily": "daily_score",
    "weekly": "weekly_score",
    "monthly": "monthly_score",
    "overall": "total_score",
}


def get_score_column(period: str):
    if period not in VALID_PERIODS:
        raise ValueError(
            "Invalid period. Use daily, weekly, monthly or overall."
        )

    return getattr(UserScore, VALID_PERIODS[period])


def get_badge(rank: int) -> str | None:
    if rank == 1:
        return "gold"

    if rank == 2:
        return "silver"

    if rank == 3:
        return "bronze"

    return None


def get_leaderboard(
    db: Session,
    period: str,
    page: int,
    page_size: int,
    current_user_id,
):
    score_column = get_score_column(period)

    total_users = db.scalar(
        select(func.count(UserScore.user_id))
    ) or 0

    total_pages = (
        (total_users + page_size - 1) // page_size
        if total_users > 0
        else 0
    )

    offset = (page - 1) * page_size

    rows = db.execute(
        select(
            User.id,
            User.username,
            score_column.label("score"),
        )
        .join(
            UserScore,
            User.id == UserScore.user_id,
        )
        .where(
            User.is_active.is_(True)
        )
        .order_by(
            desc(score_column),
            User.username,
        )
        .offset(offset)
        .limit(page_size)
    ).all()

    entries = []

    for index, row in enumerate(rows):
        rank = offset + index + 1

        entries.append(
            {
                "rank": rank,
                "username": row.username,
                "score": row.score,
                "badge": get_badge(rank),
                "is_current_user": row.id == current_user_id,
            }
        )

    current_user_rank = get_current_user_rank(
        db,
        period,
        current_user_id,
    )

    current_user_score = db.scalar(
        select(score_column)
        .join(
            User,
            User.id == UserScore.user_id,
        )
        .where(
            UserScore.user_id == current_user_id
        )
    )

    return {
        "period": period,
        "page": page,
        "page_size": page_size,
        "total_users": total_users,
        "total_pages": total_pages,
        "entries": entries,
        "current_user_rank": current_user_rank,
        "current_user_score": current_user_score or 0,
    }


def get_current_user_rank(
    db: Session,
    period: str,
    user_id,
) -> int | None:
    score_column = get_score_column(period)

    current_score = db.scalar(
        select(score_column)
        .where(
            UserScore.user_id == user_id
        )
    )

    if current_score is None:
        return None

    higher_scores = db.scalar(
        select(func.count())
        .select_from(UserScore)
        .where(
            score_column > current_score
        )
    ) or 0

    return higher_scores + 1