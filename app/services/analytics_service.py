from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.game_level import GameLevel
from app.models.game_stage import GameStage
from app.models.question import Question
from app.models.user import User
from app.models.user_progress import UserProgress


def get_admin_overview(db: Session) -> dict:
    total_users = db.scalar(
        select(func.count(User.id))
    ) or 0

    active_users = db.scalar(
        select(func.count(User.id)).where(
            User.is_active.is_(True)
        )
    ) or 0

    verified_users = db.scalar(
        select(func.count(User.id)).where(
            User.is_verified.is_(True)
        )
    ) or 0

    total_levels = db.scalar(
        select(func.count(GameLevel.id))
    ) or 0

    active_levels = db.scalar(
        select(func.count(GameLevel.id)).where(
            GameLevel.is_active.is_(True)
        )
    ) or 0

    total_stages = db.scalar(
        select(func.count(GameStage.id))
    ) or 0

    total_questions = db.scalar(
        select(func.count(Question.id))
    ) or 0

    return {
        "total_users": total_users,
        "active_users": active_users,
        "verified_users": verified_users,
        "total_levels": total_levels,
        "active_levels": active_levels,
        "total_stages": total_stages,
        "total_questions": total_questions,
    }


def get_user_activity(db: Session) -> dict:
    now = datetime.now(timezone.utc)

    one_day_ago = now - timedelta(days=1)
    thirty_days_ago = now - timedelta(days=30)

    dau = db.scalar(
        select(
            func.count(func.distinct(UserProgress.user_id))
        ).where(
            UserProgress.completed_at.is_not(None),
            UserProgress.completed_at >= one_day_ago,
        )
    ) or 0

    mau = db.scalar(
        select(
            func.count(func.distinct(UserProgress.user_id))
        ).where(
            UserProgress.completed_at.is_not(None),
            UserProgress.completed_at >= thirty_days_ago,
        )
    ) or 0

    return {
        "dau": dau,
        "mau": mau,
    }


def get_level_completion_stats(
    db: Session,
) -> list[dict]:
    rows = db.execute(
        select(
            GameLevel.id,
            GameLevel.level_number,
            GameLevel.title,
            func.count(UserProgress.id).label(
                "total_completions"
            ),
            func.coalesce(
                func.avg(UserProgress.highest_score),
                0,
            ).label("average_score"),
        )
        .outerjoin(
            GameStage,
            GameStage.level_id == GameLevel.id,
        )
        .outerjoin(
            UserProgress,
            UserProgress.stage_id == GameStage.id,
        )
        .where(
            UserProgress.status == "completed"
        )
        .group_by(
            GameLevel.id,
            GameLevel.level_number,
            GameLevel.title,
        )
        .order_by(
            GameLevel.level_number
        )
    ).all()

    return [
        {
            "level_id": str(row.id),
            "level_number": row.level_number,
            "title": row.title,
            "total_completions": row.total_completions,
            "average_score": round(
                float(row.average_score),
                2,
            ),
        }
        for row in rows
    ]


def get_popular_levels(
    db: Session,
) -> list[dict]:
    rows = db.execute(
        select(
            GameLevel.id,
            GameLevel.level_number,
            GameLevel.title,
            func.count(UserProgress.id).label(
                "attempts"
            ),
        )
        .join(
            GameStage,
            GameStage.level_id == GameLevel.id,
        )
        .join(
            UserProgress,
            UserProgress.stage_id == GameStage.id,
        )
        .group_by(
            GameLevel.id,
            GameLevel.level_number,
            GameLevel.title,
        )
        .order_by(
            func.count(UserProgress.id).desc()
        )
        .limit(10)
    ).all()

    return [
        {
            "level_id": str(row.id),
            "level_number": row.level_number,
            "title": row.title,
            "attempts": row.attempts,
        }
        for row in rows
    ]


def get_admin_analytics(
    db: Session,
) -> dict:
    return {
        "overview": get_admin_overview(db),
        "activity": get_user_activity(db),
        "level_completion": get_level_completion_stats(db),
        "popular_levels": get_popular_levels(db),
    }