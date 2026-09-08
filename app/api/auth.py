from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import RegisterRequest, UserResponse
from app.services.auth_service import register_user


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        user = register_user(db, data)

        return UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            display_name=user.display_name,
            role=user.role,
            is_verified=user.is_verified,
            is_active=user.is_active,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc