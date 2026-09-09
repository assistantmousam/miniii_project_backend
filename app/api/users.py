from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    PublicUserProfile,
    UserProfileResponse,
    UserProfileUpdate,
    UserProgressResponse,
    UserStatsResponse,
)
from app.services.user_service import (
    delete_user,
    get_user_by_username,
    get_user_progress,
    get_user_stats,
    update_user_profile,
)


router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserProfileResponse,
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        role=current_user.role,
        is_verified=current_user.is_verified,
        is_active=current_user.is_active,
    )


@router.patch(
    "/me",
    response_model=UserProfileResponse,
)
def update_my_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = update_user_profile(
        db,
        current_user,
        data,
    )

    return UserProfileResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        bio=user.bio,
        role=user.role,
        is_verified=user.is_verified,
        is_active=user.is_active,
    )


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_user(
        db,
        current_user,
    )

    return None


@router.get(
    "/{username}",
    response_model=PublicUserProfile,
)
def get_public_profile(
    username: str,
    db: Session = Depends(get_db),
):
    user = get_user_by_username(
        db,
        username,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return PublicUserProfile(
        username=user.username,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        bio=user.bio,
    )


@router.get(
    "/me/progress",
    response_model=list[UserProgressResponse],
)
def get_my_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    progress_list = get_user_progress(
        db,
        current_user.id,
    )

    return [
        UserProgressResponse(
            stage_id=str(progress.stage_id),
            level_id=str(progress.level_id),
            status=progress.status,
            score=progress.score,
            highest_score=progress.highest_score,
            attempts=progress.attempts,
            hints_used=progress.hints_used,
            time_taken=progress.time_taken,
        )
        for progress in progress_list
    ]


@router.get(
    "/me/stats",
    response_model=UserStatsResponse,
)
def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_stats(
        db,
        current_user.id,
    )