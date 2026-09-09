from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.leaderboard import LeaderboardResponse
from app.services.leaderboard_service import get_leaderboard


router = APIRouter(
    prefix="/api/v1/leaderboard",
    tags=["Leaderboard"],
)


@router.get(
    "",
    response_model=LeaderboardResponse,
)
def leaderboard(
    period: str = Query(
        default="overall",
        description="daily, weekly, monthly or overall",
    ),
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=50,
        ge=1,
        le=50,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_leaderboard(
            db=db,
            period=period.lower(),
            page=page,
            page_size=page_size,
            current_user_id=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc