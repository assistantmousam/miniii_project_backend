from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_progress import UserProgress
from app.models.user_score import UserScore
from app.schemas.user import UserProfileUpdate


def get_user_by_id(
    db: Session,
    user_id,
) -> User | None:

    return db.scalar(
        select(User).where(User.id == user_id)
    )


def get_user_by_username(
    db: Session,
    username: str,
) -> User | None:

    return db.scalar(
        select(User).where(
            User.username == username
        )
    )


def update_user_profile(
    db: Session,
    user: User,
    data: UserProfileUpdate,
) -> User:

    if data.display_name is not None:
        user.display_name = data.display_name

    if data.avatar_url is not None:
        user.avatar_url = data.avatar_url

    if data.bio is not None:
        user.bio = data.bio

    db.commit()
    db.refresh(user)

    return user


def delete_user(
    db: Session,
    user: User,
) -> None:

    user.is_active = False

    db.commit()


def get_user_progress(
    db: Session,
    user_id,
):

    return db.scalars(
        select(UserProgress)
        .where(UserProgress.user_id == user_id)
        .order_by(UserProgress.level_id)
    ).all()


def get_user_stats(
    db: Session,
    user_id,
):

    score = db.scalar(
        select(UserScore).where(
            UserScore.user_id == user_id
        )
    )

    completed_stages = db.scalar(
        select(func.count(UserProgress.id))
        .where(
            UserProgress.user_id == user_id,
            UserProgress.status == "completed",
        )
    )

    if score is None:
        return {
            "total_score": 0,
            "daily_score": 0,
            "weekly_score": 0,
            "monthly_score": 0,
            "xp": 0,
            "player_level": 1,
            "completed_stages": completed_stages or 0,
        }

    return {
        "total_score": score.total_score,
        "daily_score": score.daily_score,
        "weekly_score": score.weekly_score,
        "monthly_score": score.monthly_score,
        "xp": score.xp,
        "player_level": score.player_level,
        "completed_stages": completed_stages or 0,
    }